---
name: image-generator
description: Use this skill when a task needs to generate image files, especially for architecture diagrams, flowcharts, infographics, card-based visuals, boxed-text diagrams, explanatory graphics, or any other image output that requires layout control. It standardizes the save path, default format, file naming, text wrapping, boundary control, self-check flow, and final response format.
---

# Image Generator

## 概述

当任务需要生成图片文件时，使用这个 skill。它的目标不是决定图片内容本身，而是统一图片的输出规范，确保文件保存位置、格式、命名、文本排版和最终交付方式始终一致。

## 默认输出规则

除非用户明确指定其他要求，否则始终遵循以下规则：

- 图片默认保存到 `/Users/edy/Downloads/AI/images`
- 优先使用 `PNG` 格式
- 保存前如果目录不存在，先创建目录
- 文件名使用有语义的英文名
- 如果存在覆盖风险，在文件名中追加日期或时间戳
- 在回复中始终返回图片的绝对路径
- 图片中不要备注数据参考来源

## 排版规则

对于带框和文字的图片，必须满足：

- 文字始终位于框内
- 默认自动换行
- 避免文字重叠
- 避免文字截断
- 避免压线
- 避免超出画布
- 避免因为字号过大导致局部不可读
- 避免因为内容过密导致整体难以辨认

如果图片包含多个卡片、分区、泳道、节点或说明块，优先通过增加留白、调整分组和重新布局来改善可读性，而不是只是一味缩小字体。

## 自检要求

所有带排版的图片在输出前都必须先自检。

重点检查：

- 是否存在文字重叠
- 是否存在文字过密
- 是否存在越界
- 是否存在难以辨认的字号或对比度
- 是否有框内文字没有完整显示
- 是否有元素之间间距过小导致阅读困难

如果发现上述问题，必须先调整后再输出。优先调整方式包括：

- 缩小字号
- 调整行高
- 增加卡片高度
- 增加卡片宽度
- 增加模块间距
- 增大整体画布尺寸
- 重新安排布局方向

## 文件命名规则

文件名应当：

- 使用英文
- 具有语义
- 尽量反映图片内容
- 在必要时追加日期或时间戳避免覆盖

推荐命名示例：

- `system-architecture-20260421.png`
- `go-package-flow.png`
- `user-login-sequence-20260421-153000.png`

避免使用：

- `image1.png`
- `final-final.png`
- `新建图片.png`

## 工作流

### 1. 确认输出目标

先确认这次任务是否真的需要生成图片文件，而不是只返回 Mermaid、SVG 代码或纯文本说明。

### 2. 准备输出目录

如果目标目录不存在，先创建：

- `/Users/edy/Downloads/AI/images`

### 3. 生成图片

根据任务选择合适的绘图方式，但必须遵循本 skill 的输出规则。

### 4. 自检排版

在交付前逐项检查文字是否在框内、是否自动换行、是否清晰可读。

### 5. 返回结果

最终回复中必须包含图片的绝对路径。

## 决策规则

- 如果用户没有指定格式，默认导出 PNG
- 如果用户没有指定输出目录，默认保存到 `/Users/edy/Downloads/AI/images`
- 如果已有同名文件且存在覆盖风险，主动追加时间戳
- 如果图片包含大量文字，优先增大画布或拆分布局，不要直接硬塞进原尺寸
- 如果只是轻微拥挤，也要优先调整到可读，而不是勉强输出

## 提示词示例

- `Use $image-generator to generate this image and save it with the default rules.`
- `Use $image-generator to export a PNG image with automatic naming, wrapping, and layout self-check.`
- `Use $image-generator to export this diagram to the default directory and return the absolute path.`
