# Personal Codex Skills Repo

这个仓库位于 `/Users/edy/.codex/skills`，目的是在不影响 Codex 自动发现 skill 的前提下，只管理你自己创建的 skill。

## 设计原则

- Codex 会自动从 `~/.codex/skills` 下读取 skill。
- 为了保持自动关联，自定义 skill 仍然直接放在这个目录的一级子目录下。
- 系统自带或第三方 skill 默认不纳入 git 管理。
- 当前已纳入管理的自定义 skill：`architecture-diagrams`
- 以后新建的个人 skill，建议统一使用 `user-` 前缀，例如：`user-go-development`

## 当前规则

`.gitignore` 默认忽略全部内容，只放行：

- `.gitignore`
- `README.md`
- `architecture-diagrams`
- 所有 `user-*` 命名的 skill 目录

## 推荐用法

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
