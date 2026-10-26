# 百炼 Agent 1.0 创建、发布与接入

本指南依据 2026-10-26 查阅的[阿里云 Agent 1.0 官方文档](https://docs.agent.bailian.aliyun.com/zh/flow-agent/applications/agent-app-legacy)。界面可能调整，以控制台实际显示为准。

1. 登录[百炼旧版控制台](https://bailian-legacy.console.aliyun.com/)。官方说明 Agent 1.0 仅在旧版控制台创建；新版入口底部也可能提供“旧版 Agent 创建入口”。不要创建成 Agent 2.0 或工作流应用。
2. 选择北京地域及目标工作空间，进入应用管理，创建“智能体应用”，命名“小龙虾实验助手 FlowAgent 1.0”。
3. 选择可用的千问 Plus 模型，推荐温度 0.2、上下文 10 轮；这些是本项目建议值，可按模型实际限制调整。
4. 将 `prompts/flowagent_system.md` 全文粘贴至系统提示词。该配置不是可导入的工作流 DSL。
5. 本地工具实验无需启用云端插件或知识库。云端插件在云端执行，不能访问电脑的 `workspace/`。如果另行启用 RAG，请在设计报告中注明真实知识源，不要声称本项目已建知识库。
6. 在控制台调试“你好”和 JSON 动作输出，然后点击右上角“发布”，确认发布版本。保存成功或调试通过不等于发布完成。
7. 从应用详情或发布渠道获取应用 ID；在同地域、同工作空间下创建或选择有调用权限的 DashScope API Key。
8. 将 `.env.example` 复制为 `.env`，只在本地填写 `DASHSCOPE_API_KEY`、`BAILIAN_APP_ID`。子工作空间按需填写 `BAILIAN_WORKSPACE_ID`。
9. 启动网页，点击“重新加载配置 / 新对话”。用普通聊天验证流式输出和多轮记忆，再用工具模式创建、读取、压缩文件。
10. 运行 `python -m scripts.smoke_cloud` 验证实际云端会话。把不含 Key 的应用类型、发布时间、应用 ID 和请求 ID 记录到交付状态；不要把 API Key 页面截图上传仓库。

发布后应用 API 调用最新发布版本；修改草稿后需重新发布。系统提示词大幅变化后开始新会话。

## 排障

| 现象 | 检查 |
|---|---|
| 网页聊天框禁用 | `.env` 两个必填值是否存在，是否重新加载 |
| 401/403 | Key 是否有效、有权限、地域与空间匹配 |
| 应用不存在或无法调用 | 应用 ID、Agent 类型、北京地域及发布状态 |
| 多轮忘记上下文 | 是否换模式或清空会话；服务端会话是否已过期 |
| 工具模式只聊天 | 已发布系统提示词是否允许 JSON 动作协议 |
| shell 报错找不到命令 | 依赖命令是否已安装；Windows 和 Linux 语法不同 |

接口依据：[工作流与旧版智能体应用 API](https://help.aliyun.com/zh/model-studio/agent-and-workflow-application-api-reference)。本项目不调用未公开的控制台创建接口。
