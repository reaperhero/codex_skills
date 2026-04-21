#!/usr/bin/env python3
"""
Detect Go pprof routes from the current repository, probe a running service,
and capture lightweight CPU or memory profiles for first-pass diagnosis.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path


ROUTE_RE = re.compile(r'["\'](?P<route>/[^"\']*pprof[^"\']*)["\']')
PARTY_RE = re.compile(r"\b(?:Party|Group)\(\s*[\"'](?P<route>/[^\"']*pprof[^\"']*)[\"']")
HANDLER_RE = re.compile(r"pprof\.Handler\(\s*[\"'](?P<name>[^\"']+)[\"']\s*\)")

COMMON_ENDPOINTS = [
    "/",
    "/cmdline",
    "/profile",
    "/symbol",
    "/trace",
    "/heap",
    "/allocs",
    "/goroutine",
    "/threadcreate",
    "/block",
    "/mutex",
]


@dataclass
class RouteEvidence:
    file: str
    line: int
    route: str
    kind: str
    snippet: str


@dataclass
class Detection:
    base_route: str
    evidence: list[RouteEvidence] = field(default_factory=list)
    activation_start: str | None = None
    activation_status: str | None = None
    activation_stop: str | None = None
    profile_names: list[str] = field(default_factory=list)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    detect = subparsers.add_parser("detect", help="Detect likely pprof routes from a Go repository")
    detect.add_argument("--repo", default=".", help="Repository root to scan")
    detect.add_argument("--json", action="store_true", help="Print JSON output")

    probe = subparsers.add_parser("probe", help="Probe a running service using auto-detected pprof routes")
    probe.add_argument("--repo", default=".", help="Repository root to scan")
    probe.add_argument("--base-url", required=True, help="Service base URL such as http://127.0.0.1:8080")
    probe.add_argument("--route", help="Explicit pprof base route; defaults to detected route")
    probe.add_argument("--timeout", type=float, default=5.0, help="HTTP timeout in seconds")
    probe.add_argument("--json", action="store_true", help="Print JSON output")

    capture = subparsers.add_parser("capture", help="Capture and summarize pprof data from a running service")
    capture.add_argument("--repo", default=".", help="Repository root to scan")
    capture.add_argument("--base-url", required=True, help="Service base URL such as http://127.0.0.1:8080")
    capture.add_argument("--route", help="Explicit pprof base route; defaults to detected route")
    capture.add_argument(
        "--profile",
        choices=["cpu", "heap", "allocs", "goroutine", "mutex", "block", "both"],
        default="both",
        help="Profile type to capture",
    )
    capture.add_argument("--seconds", type=int, default=30, help="CPU sampling duration in seconds")
    capture.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout in seconds")
    capture.add_argument("--out-dir", help="Directory to store captured profiles")
    capture.add_argument("--json", action="store_true", help="Print JSON output")

    return parser.parse_args()


def iter_go_files(repo: Path) -> list[Path]:
    paths: list[Path] = []
    for path in repo.rglob("*.go"):
        if ".git" in path.parts or "vendor" in path.parts:
            continue
        paths.append(path)
    return sorted(paths)


def detect_routes(repo: Path) -> list[Detection]:
    detections: list[Detection] = []
    by_route: dict[str, Detection] = {}

    for path in iter_go_files(repo):
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue

        joined = "\n".join(lines)
        if "pprof" not in joined:
            continue

        file_routes = collect_file_routes(lines)
        fallback_route = file_routes[0] if file_routes else "/debug/pprof"

        for idx, line in enumerate(lines, start=1):
            party_match = PARTY_RE.search(line)
            matches: list[tuple[str, re.Match[str] | None]] = [
                ("party", party_match),
                ("route", None if party_match else ROUTE_RE.search(line)),
            ]

            for kind, match in matches:
                if not match:
                    continue
                route = normalize_route(match.group("route"))
                detection = by_route.setdefault(route, Detection(base_route=route))
                evidence = RouteEvidence(
                    file=str(path),
                    line=idx,
                    route=route,
                    kind=kind,
                    snippet=line.strip(),
                )
                if evidence not in detection.evidence:
                    detection.evidence.append(evidence)

            if "/start" in line and "pprof" in joined:
                for route in file_routes or [fallback_route]:
                    detection = by_route.setdefault(route, Detection(base_route=route))
                    detection.activation_start = normalize_route(route + "/start")
            if "/status" in line and "pprof" in joined:
                for route in file_routes or [fallback_route]:
                    detection = by_route.setdefault(route, Detection(base_route=route))
                    detection.activation_status = normalize_route(route + "/status")
            if "/stop" in line and "pprof" in joined:
                for route in file_routes or [fallback_route]:
                    detection = by_route.setdefault(route, Detection(base_route=route))
                    detection.activation_stop = normalize_route(route + "/stop")

            handler = HANDLER_RE.search(line)
            if handler:
                profile_name = handler.group("name")
                route = fallback_route
                detection = by_route.setdefault(route, Detection(base_route=route))
                if profile_name not in detection.profile_names:
                    detection.profile_names.append(profile_name)

    detections = sorted(by_route.values(), key=score_detection, reverse=True)
    return detections


def route_candidates_from_text(text: str) -> list[str]:
    routes = [normalize_route(match.group("route")) for match in PARTY_RE.finditer(text)]
    routes.extend(normalize_route(match.group("route")) for match in ROUTE_RE.finditer(text))
    unique: list[str] = []
    for route in routes:
        base = route.split("/start")[0].split("/status")[0].split("/stop")[0]
        if "pprof" in base and base not in unique:
            unique.append(normalize_route(base))
    return unique


def collect_file_routes(lines: list[str]) -> list[str]:
    unique: list[str] = []
    for line in lines:
        candidates = route_candidates_from_text(line)
        for candidate in candidates:
            if candidate not in unique:
                unique.append(candidate)
    return unique


def normalize_route(route: str) -> str:
    route = "/" + route.strip().strip("/ ")
    route = re.sub(r"/{2,}", "/", route)
    return route.rstrip("/") if route != "/" else route


def score_detection(item: Detection) -> tuple[int, int, int]:
    score = 0
    if item.activation_start or item.activation_status:
        score += 3
    if item.profile_names:
        score += 2
    score += len(item.evidence)
    return score, len(item.profile_names), -len(item.base_route)


def print_detection(detections: list[Detection], as_json: bool) -> int:
    if as_json:
        print(json.dumps([asdict(item) for item in detections], ensure_ascii=False, indent=2))
        return 0

    if not detections:
        print("No pprof route detected from repository scan.")
        return 1

    for item in detections:
        print(f"base_route: {item.base_route}")
        if item.activation_status:
            print(f"  status: {item.activation_status}")
        if item.activation_start:
            print(f"  start:  {item.activation_start}")
        if item.activation_stop:
            print(f"  stop:   {item.activation_stop}")
        if item.profile_names:
            print(f"  handlers: {', '.join(item.profile_names)}")
        for evidence in item.evidence[:3]:
            print(f"  evidence: {evidence.file}:{evidence.line}  {evidence.snippet}")
        print()
    return 0


def join_url(base_url: str, path: str) -> str:
    return urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def http_get(url: str, timeout: float) -> tuple[int, str]:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
            return response.getcode(), body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body
    except urllib.error.URLError as exc:
        raise RuntimeError(f"request failed for {url}: {exc}") from exc


def choose_detection(repo: Path, explicit_route: str | None) -> Detection:
    if explicit_route:
        return Detection(base_route=normalize_route(explicit_route))

    detections = detect_routes(repo)
    if detections:
        return detections[0]
    return Detection(base_route="/debug/pprof")


def probe_service(repo: Path, base_url: str, explicit_route: str | None, timeout: float) -> dict[str, object]:
    detection = choose_detection(repo, explicit_route)
    result: dict[str, object] = {
        "base_url": base_url,
        "detected_route": detection.base_route,
        "activated": False,
        "probes": [],
    }

    if detection.activation_status:
        status_url = join_url(base_url, detection.activation_status)
        status_code, status_body = http_get(status_url, timeout)
        result["status_url"] = status_url
        result["status_code"] = status_code
        result["status_body"] = status_body.strip()

        if "not running" in status_body.lower() and detection.activation_start:
            start_url = join_url(base_url, detection.activation_start)
            start_code, start_body = http_get(start_url, timeout)
            result["start_url"] = start_url
            result["start_code"] = start_code
            result["start_body"] = start_body.strip()
            result["activated"] = start_code < 400

    for endpoint in COMMON_ENDPOINTS:
        probe_url = join_url(base_url, detection.base_route + endpoint)
        try:
            code, body = http_get(probe_url, timeout)
            result["probes"].append(
                {
                    "endpoint": detection.base_route + endpoint,
                    "url": probe_url,
                    "status": code,
                    "ok": code < 400,
                    "preview": body[:120].strip(),
                }
            )
        except RuntimeError as exc:
            result["probes"].append(
                {
                    "endpoint": detection.base_route + endpoint,
                    "url": probe_url,
                    "status": 0,
                    "ok": False,
                    "preview": str(exc),
                }
            )

    return result


def ensure_out_dir(path: str | None) -> Path:
    if path:
        out_dir = Path(path).expanduser()
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir
    return Path(tempfile.mkdtemp(prefix="go-pprof-debug-"))


def download_binary(url: str, output: Path, timeout: float) -> None:
    request = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            output.write_bytes(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"download failed for {url}: HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"download failed for {url}: {exc}") from exc


def run_pprof(profile: Path, sample_type: str | None = None) -> str:
    cmd = ["go", "tool", "pprof", "-top"]
    if sample_type:
        cmd.extend(["-sample_index", sample_type])
    cmd.append(str(profile))
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"go tool pprof failed: {' '.join(cmd)}")
    return result.stdout.strip()


def profile_targets(profile: str) -> list[tuple[str, str | None]]:
    if profile == "cpu":
        return [("profile", None)]
    if profile == "heap":
        return [("heap", "inuse_space")]
    if profile == "allocs":
        return [("allocs", "alloc_space")]
    if profile in {"goroutine", "mutex", "block"}:
        return [(profile, None)]
    return [("profile", None), ("heap", "inuse_space"), ("allocs", "alloc_space")]


def capture_profiles(
    repo: Path,
    base_url: str,
    explicit_route: str | None,
    profile: str,
    seconds: int,
    timeout: float,
    out_dir: Path,
) -> dict[str, object]:
    probe = probe_service(repo, base_url, explicit_route, timeout)
    detection = choose_detection(repo, explicit_route)
    captures: list[dict[str, object]] = []

    for target, sample_index in profile_targets(profile):
        if target == "profile":
            url = join_url(base_url, f"{detection.base_route}/profile?seconds={seconds}")
            suffix = "cpu.pb.gz"
        else:
            url = join_url(base_url, f"{detection.base_route}/{target}")
            suffix = f"{target}.pb.gz"

        output = out_dir / suffix
        download_binary(url, output, timeout=max(timeout, seconds + 5 if target == "profile" else timeout))
        summary = run_pprof(output, sample_type=sample_index)
        captures.append(
            {
                "target": target,
                "sample_index": sample_index,
                "url": url,
                "file": str(output),
                "summary": summary,
            }
        )

    return {
        "probe": probe,
        "captures": captures,
        "out_dir": str(out_dir),
    }


def print_probe(result: dict[str, object], as_json: bool) -> int:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print(f"detected_route: {result['detected_route']}")
    if "status_url" in result:
        print(f"status: {result['status_url']} -> {result['status_code']} {result.get('status_body', '')}")
    if "start_url" in result:
        print(f"start:  {result['start_url']} -> {result['start_code']} {result.get('start_body', '')}")
    for probe in result["probes"]:
        marker = "OK" if probe["ok"] else "FAIL"
        print(f"{marker:4} {probe['status']:>3} {probe['endpoint']}  {probe['preview']}")
    return 0


def print_capture(result: dict[str, object], as_json: bool) -> int:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    print_probe(result["probe"], as_json=False)
    print(f"\nout_dir: {result['out_dir']}")
    for item in result["captures"]:
        print(f"\n===== {item['target']} =====")
        print(f"file: {item['file']}")
        if item["sample_index"]:
            print(f"sample_index: {item['sample_index']}")
        print(item["summary"])
    return 0


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).expanduser().resolve()

    try:
        if args.command == "detect":
            detections = detect_routes(repo)
            return print_detection(detections, args.json)

        if args.command == "probe":
            result = probe_service(repo, args.base_url, args.route, args.timeout)
            return print_probe(result, args.json)

        if args.command == "capture":
            out_dir = ensure_out_dir(args.out_dir)
            result = capture_profiles(repo, args.base_url, args.route, args.profile, args.seconds, args.timeout, out_dir)
            return print_capture(result, args.json)
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
