# Go 测试补充规范

当主技能里的测试规则还不够覆盖当前任务时，再读取本文件。

## 目标

测试应优先做到：
- 小
- 稳定
- 快
- 可定位失败原因

## 推荐模式

优先使用 table-driven tests：

```go
tests := []struct {
    name string
    input string
    want string
}{
    {
        name:  "basic",
        input: "a",
        want:  "b",
    },
}

for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        got := fn(tt.input)
        if got != tt.want {
            t.Fatalf("fn() = %v, want %v", got, tt.want)
        }
    })
}
```

## 覆盖重点

优先考虑：
- 空输入
- nil 输入
- 单元素
- 重复值
- 顺序保持
- 去重逻辑
- 边界值
- 错误路径
- 已有值保持不变

## 避免事项

- 不要为小逻辑引入复杂 mock
- 不要依赖真实网络或外部服务
- 不要让测试依赖运行顺序
- 不要写难以读懂的断言信息
