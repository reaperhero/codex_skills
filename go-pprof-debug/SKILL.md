---
name: go-pprof-debug
description: 当用户希望通过 pprof 排查 Go 服务的 CPU、内存、goroutine、锁竞争或阻塞问题时使用。适用于“用 pprof 排查 CPU”、“分析内存泄漏”、“自动识别当前项目的 pprof 路由”、“抓取 profile 后分析热点并回到代码给出原因和解决方案”等场景。
---

# Go Pprof Debug

## 概述

当任务目标是用 `pprof` 实际排查 Go 服务问题，而不是只解释 `pprof` 概念时，使用这个 skill。

默认工作流固定为 4 步：

1. 先从当前仓库里找到 `pprof` 路由
2. 再调用在线 `pprof` 接口抓取运行时证据
3. 基于 `pprof` 输出先诊断问题类型和热点
4. 最后再回到代码定位原因，并给出修复方案

这个顺序很重要。不要一上来先读代码猜“哪里可能泄漏”，而要先让运行时证据缩小范围，再进入代码。

## 期望输入

优先接受以下任一输入：

- 一个正在运行的服务地址，例如 `http://127.0.0.1:8080`
- 一个主机地址，外加可能的端口或路由提示
- 一个直接可访问的 `pprof` URL
- 只有当前仓库，此时第一目标是自动识别 `pprof` 路由

可选输入：

- profile 类型：`cpu`、`heap`、`allocs`、`goroutine`、`mutex`、`block`、`both`
- CPU 采样时长，通常 `15-30` 秒
- profile 文件输出目录

如果用户没有提供路由，先从当前仓库自动识别，不要直接假设一定是 `/debug/pprof`。

## 工作流

### 1. 先找仓库里的 pprof 路由

先执行：

```bash
python3 /Users/edy/.codex/skills/go-pprof-debug/scripts/go_pprof_debug.py detect --repo .
```

探测器会重点搜索：

- `net/http/pprof`
- `pprof.Handler(...)`
- 诸如 `"/debug/pprof"` 的字面路由
- 可能的控制接口，例如 `/start`、`/status`、`/stop`

这一步的目标是明确回答：

- 哪个路由最可能暴露了 `pprof`
- 这个路由是默认开启，还是可能需要先启用
- 哪个文件能证明这个路由存在

如果用户只给了一个主机地址，也不要跳过这一步。先从仓库出发建立第一手证据。

### 2. 再调用 pprof 抓运行时证据

如果用户给了服务地址，继续探测：

```bash
python3 /Users/edy/.codex/skills/go-pprof-debug/scripts/go_pprof_debug.py probe \
  --repo . \
  --base-url http://127.0.0.1:8080
```

行为规则：

- 如果仓库提示有状态接口，先探测状态
- 如果看起来 `pprof` 未开启，但仓库里有 `/start` 之类的控制接口，可以尝试启用
- 然后探测 `pprof` 首页和关键 profile 端点

不要默认路由一定是 `/debug/pprof`，优先让仓库检测结果来驱动探测。

确认路由可用后，根据问题类型抓取对应 profile：

- `cpu`：适用于 CPU 高、请求慢、热点循环
- `heap`：适用于当前堆内存持续上涨
- `allocs`：适用于排查累计分配量和分配抖动
- `goroutine`：适用于怀疑 goroutine 泄漏
- `mutex` / `block`：适用于锁竞争和阻塞问题

这一阶段的重点是“先拿到运行时证据”。优先依据 `pprof` 输出、`/stats`、运行时 profile 做判断，而不是先看源码猜测。

### 3. 基于 pprof 输出先诊断问题

抓 CPU：

```bash
python3 /Users/edy/.codex/skills/go-pprof-debug/scripts/go_pprof_debug.py capture \
  --repo . \
  --base-url http://127.0.0.1:8080 \
  --profile cpu \
  --seconds 30
```

抓内存：

```bash
python3 /Users/edy/.codex/skills/go-pprof-debug/scripts/go_pprof_debug.py capture \
  --repo . \
  --base-url http://127.0.0.1:8080 \
  --profile heap
```

同时抓多类：

```bash
python3 /Users/edy/.codex/skills/go-pprof-debug/scripts/go_pprof_debug.py capture \
  --repo . \
  --base-url http://127.0.0.1:8080 \
  --profile both
```

默认分析方式使用 `go tool pprof -top`。

解释时的优先关注点：

- `cpu`：看 flat 和 cumulative 热点，关注忙循环、重复序列化、哈希、反射、锁竞争
- `heap`：优先看 `inuse_space`，确认谁在当前持有内存
- `allocs`：用来看谁历史累计分配最多
- `goroutine`：看是否存在 goroutine 堆积、阻塞或泄漏

这一阶段要先回答：

- 问题主要是 CPU、堆内存保留、分配抖动，还是 goroutine 堆积
- 是单一主热点，还是多个热点共同作用
- 问题是否稳定、可复现
- 哪些结论是 profile 直接证明的，哪些只是工程推断

在运行时症状没有收敛到某个热点之前，不要急着回源码。

### 4. 最后回到代码，解释原因并给出修复方案

当 `pprof` 已经缩小到明确热点后，再做代码映射：

- 在本地仓库搜索热点函数名
- 阅读最小必要范围的相关包和调用链
- 把热点映射到尽量小的代码区域
- 解释根因
- 给出一个或多个修复方向

理想顺序是：

1. 路由发现
2. 在线 `pprof` 抓证据
3. 运行时诊断
4. 回到代码定位原因和解决方案

如果用户明确要求修复，就继续做代码改动和验证。

## 决策规则

以下情况可以自主继续：

- 仓库里清楚暴露了候选 `pprof` 路由
- 服务可访问
- 抓到的 profile 已经有明显热点

以下情况才暂停并询问用户：

- 没有可访问的服务，也没有现成的 profile 文件
- 有多个候选服务，贸然选择风险较高
- 启用 `pprof` 可能影响生产环境，而用户没有授权这样做

如果被阻塞，只问一个简短、具体的问题。

不要采用“先读代码猜哪里泄漏”的路径。只有在 profile 已经指向具体热点后，才深入阅读代码。

## 输出要求

总结时应包含：

- 识别到的 `pprof` 路由，以及对应证据文件
- 抓取了哪些 profile
- profile 中最主要的热点及占比
- 基于 `pprof` 的运行时诊断结论
- 热点映射回本地代码的位置
- 可能的根因
- 建议的修复方向
- 如果相关，说明是否需要额外激活 `pprof`

要明确区分：

- 哪些内容是 `pprof` 直接证明的
- 哪些内容是基于证据做出的合理推断

## 提示词示例

- `Use $go-pprof-debug 自动识别当前项目的 pprof 路由，并探测本地 8080 服务。`
- `Use $go-pprof-debug 抓这个 Go 服务 30 秒 CPU profile，然后总结热点。`
- `Use $go-pprof-debug 分析 heap 和 allocs，看内存是不是缓存或 goroutine 泄漏。`
- `Use $go-pprof-debug 先找 pprof 路由，再抓 heap，分析问题后回到代码里给出原因和解决方案。`

## 资源

- 使用 `scripts/go_pprof_debug.py` 完成路由识别、在线探测、profile 抓取和 `pprof` 汇总
