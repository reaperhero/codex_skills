# Personal Codex Skills Repo

这个仓库位于 `/Users/edy/.codex/skills`，目的是在不影响 Codex 自动发现 skill 的前提下，只管理你自己创建的 skill。

## 设计原则

- Codex 会自动从 `~/.codex/skills` 下读取 skill。
- 为了保持自动关联，自定义 skill 仍然直接放在这个目录的一级子目录下。
- 系统自带或第三方 skill 默认不纳入 git 管理。
- 当前已纳入管理的自定义 skill：`architecture-diagrams`、`go-development`、`go-pprof-debug`、`image-generator`、`log-fix-branch`、`word-doc-optimizer`
- 以后新建的个人 skill，建议统一使用 `user-` 前缀，例如：`user-go-development`

## 当前规则

`.gitignore` 当前默认忽略全部内容，新加入的自定义 skill 默认放行：

- `.gitignore`
- `README.md`
- `go-development`
- `image-generator`
- 所有 `user-*` 命名的 skill 目录

说明：

- `architecture-diagrams`、`go-pprof-debug`、`log-fix-branch`、`word-doc-optimizer` 已经是仓库中的既有跟踪目录，因此虽然不在当前默认放行列表里，仍然会继续被 git 管理

## 当前已关联 Skill

下表记录当前这个仓库里已经在用、并且和你日常工作直接相关的自定义 skill。

| Skill | 作用 | 典型用法 | 适用场景 |
| --- | --- | --- | --- |
| `architecture-diagrams` | 输出物理架构图和部署架构图，支持文字版与图片版，并遵循你的图片排版规则。 | `使用 $architecture-diagrams 绘制当前系统，并同时输出物理架构图和部署架构图。` | 读 README、代码结构、服务清单、部署说明后，生成系统架构图。 |
| `go-development` | 统一 Go 开发流程，强调先读代码、最小改动、按仓库风格写测试和定向验证。 | `Use $go-development 修复当前包里的 bug，并补充聚焦测试。` | Go 代码实现、重构、排错、补测试、分析包结构。 |
| `go-pprof-debug` | 约束基于 `pprof` 的排障流程，先自动识别路由、再抓运行时证据、最后回到代码定位热点和根因。 | `使用 $go-pprof-debug 分析这个 Go 服务的 CPU 和 heap 问题。` | Go 服务 CPU 飙高、内存上涨、goroutine 泄漏、锁竞争、阻塞问题排查。 |
| `image-generator` | 统一图片文件输出规范，包括默认路径、PNG 格式、命名、自动换行、排版自检和绝对路径返回。目录为 `image-generator`。 | `Use $image-generator to generate this image and save it with the default rules.` | 架构图、流程图、卡片图、说明图等需要导出图片文件的任务。 |
| `log-fix-branch` | 固定“先读日志、再定位代码、直接修当前分支并最小验证”的闭环流程。 | `使用 $log-fix-branch 根据这个日志样本排查并修复当前分支。` | 本地日志、挂载日志、SSH 远端日志、`journalctl` 输出驱动的 bug 修复。 |
| `word-doc-optimizer` | 优化 Word 文档内容与结构，兼顾语义保留、正式文风、标题层级和 `.docx` 交付修复。 | `使用 $word-doc-optimizer 优化这份周报，并保持原有标题层级。` | 报告、通知、方案、会议纪要、SOP、简历、正式业务文档润色与结构修复。 |

## 使用建议

- 需要画图时，优先组合使用 `architecture-diagrams` 和 `image-generator`
- 需要改 Go 代码时，优先使用 `go-development`
- 需要用 `pprof` 抓运行时证据排查 Go 服务时，使用 `go-pprof-debug`
- 需要根据日志直接修当前分支时，使用 `log-fix-branch`
- 需要优化 Word 文档或修复 `.docx` 结构时，使用 `word-doc-optimizer`
- 需要输出 PNG、并保证文字不越界时，使用 `image-generator`

## 推荐新增方式

创建新的个人 skill 时，直接在 `/Users/edy/.codex/skills` 下创建目录，例如：

- `/Users/edy/.codex/skills/user-go-development`
- `/Users/edy/.codex/skills/user-architecture-review`

这样可以同时满足：

- Codex 自动识别
- git 仓库自动纳管
- 系统 skill 不被误加入仓库

## 如果你想纳管一个旧的自定义 skill

有两种方式：

1. 把它重命名为 `user-*`
2. 在 `.gitignore` 里单独加入放行规则



## 其他skill

UI UX Pro Max

Superpowers