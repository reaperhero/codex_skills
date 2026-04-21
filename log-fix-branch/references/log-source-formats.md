# Log Source Formats

Use these formats when invoking `log-fix-branch`.

## Local Sources

- Single file: `/var/log/myapp/error.log`
- Compressed file: `/var/log/myapp/error.log.gz`
- Directory: `/var/log/myapp/`

When given a directory, prefer the newest `*.log`, `*.log.*`, `*.out`, or `*.txt` files first.

## Remote Sources

- SCP-style path: `deploy@10.0.0.8:/data/logs/api/error.log`
- SSH URL: `ssh://deploy@api-prod-1/data/logs/api/error.log`
- Remote directory: `deploy@api-prod-1:/data/logs/api/`

Use remote access only for reading logs. Do not patch code or configs on the remote machine unless the user explicitly asks for that and the risk is understood.

## Explicit Read Commands

If the logs do not live in files, the user can provide a command instead.

Examples:

```bash
ssh api-prod 'journalctl -u checkout -n 300 --no-pager'
ssh worker-2 'docker logs --tail 300 order-worker'
kubectl logs deploy/api -n prod --tail=300
```

When the user provides a command, run it as read-only input for diagnosis, then make code changes in the local repository.

## Good User Prompts

- `Use $log-fix-branch. 日志在 /tmp/app.log，直接修当前分支。`
- `Use $log-fix-branch. 日志在 ops@172.16.0.8:/srv/logs/gateway/error.log，分析后改代码。`
- `Use $log-fix-branch. 执行 ssh api-prod 'journalctl -u pay -n 500 --no-pager'，然后在当前分支修复。`

## Investigation Order

1. Confirm the branch and worktree state.
2. Read a small log sample.
3. Find the strongest failure signal.
4. Map that signal to code.
5. Patch the current branch.
6. Run the narrowest useful verification.
