# AI-TestFlow 测试工程师 Agent 三阶段演进路线

## 1. 目标

AI-TestFlow 的目标不是优先生成自动化脚本，而是模拟测试工程师拿到新需求后的真实工作：检索测试知识、分析风险、设计探索目标、操作真实系统、收集证据、判断缺陷，最后再把已经验证稳定的路径沉淀为回归脚本。

统一流程如下：

```text
PRD / 功能文档
  -> Knowledge Agent
  -> Requirement Agent
  -> Test Design Agent
  -> API Agent / Browser Agent
  -> Analysis Agent
  -> Report Agent / Bug Agent
  -> Automation Agent
```

Demo 系统只是被测对象，Agent 主流程不得包含登录注册专用规则，也不得读取缺陷基准文件。

## 2. 阶段一：Structured Browser Agent

阶段一不接入视觉模型。Browser Agent 从真实运行页面读取结构化观察：

- 当前 URL 和页面标题。
- 页面可见文本。
- Accessibility Tree。
- 输入框、按钮、链接等可交互控件。
- Console 错误和失败的网络请求。
- 仅保存为证据、不发送给模型的页面截图。

大模型每次根据最新观察决定一个语义动作，Playwright Controller 负责执行。允许的定位方式只有 `role`、`label`、`text` 和 `placeholder`，不允许模型输出 CSS Selector、XPath、JavaScript 或完整 Playwright 脚本。

API Agent 同样采用实时方式，通过 HTTP Controller 连续发送结构化请求并维护 Cookie。接口和页面任务完成后，Automation Agent 只将 `passed` 轨迹转成 pytest 或 Playwright 回归脚本。

阶段一是当前实现阶段，也是后续实验的基线。

## 3. 阶段二：Vision Browser Agent

阶段二保持测试任务、执行状态和报告格式不变，新增视觉 Observer：

```text
浏览器截图
  -> 视觉模型理解页面布局和控件
  -> Browser Agent 决定目标与动作
  -> Browser Controller 执行坐标或视觉目标操作
```

视觉模型只负责页面观察，不替代需求分析、知识检索、测试设计、结果判断和证据管理。具体模型供应商在阶段二实施前按当时可用 API 单独选择，不与阶段一的 DeepSeek 文本模型配置绑定。

## 4. 阶段三：Hybrid Browser Agent

阶段三同时使用截图视觉信息和结构化页面信息：

```text
Screenshot Observation
        +
Accessibility / DOM Observation
        -> Unified Observation
        -> Browser Agent
```

视觉信息用于理解布局、图标、画布和缺少语义标记的控件；Accessibility 和页面文本用于稳定定位、输入和断言。两类信息冲突时必须保留冲突记录，并由 Analysis Agent 判断属于页面可访问性问题、Agent 执行问题还是产品缺陷。

## 5. 统一 Observer 接口

三种模式共用同一执行记录结构：

```text
observation_id
execution_id
step
current_url
page_title
visible_text
accessibility_snapshot
interactive_elements
console_errors
failed_requests
screenshot_path
vision_description
```

阶段一的 `vision_description` 为空，截图路径不会进入大模型输入；阶段二和阶段三才允许视觉模型读取截图。这样可以在不修改测试任务和分析链路的情况下切换观察方式。

## 6. 对照实验

Structured、Vision 和 Hybrid 使用同一份 PRD、同一批测试任务、相同初始数据库、相同最大步骤数和独立浏览器会话。缺陷基准只在评估阶段读取，不进入 Agent 上下文。

需要记录：

- 测试任务完成率。
- 已知缺陷发现率。
- 误报率。
- `blocked` 任务比例。
- 平均动作数和平均运行时间。
- LLM 调用次数、Token 和 API 成本。
- 页面结构变化后的恢复率。

每次实验保存完整动作、观察、截图、分类和报告，不能只比较最终 Bug 数量。

## 7. 阶段验收

阶段一完成条件：实时 API 和浏览器测试不依赖预生成脚本，能够在通用页面上完成观察与操作，并将通过轨迹沉淀为回归脚本。

阶段二完成条件：视觉模型可以只根据截图完成相同测试任务，并输出与阶段一一致的执行记录。

阶段三完成条件：混合观察能够处理纯结构化或纯视觉模式无法稳定完成的页面，并提供可量化的效果对比。
