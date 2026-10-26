# 百炼 FlowAgent 1.0 × Streamlit 小龙虾实验室

阿里云百炼旧版智能体应用调用、本地工具执行循环，以及《深入理解 AI Agent：设计原理与工程实践》的设计分析。

参考视频：[飞天闪客《20 行代码彻底搞懂小龙虾！》](https://www.bilibili.com/video/BV19hwTzwETF/)。本仓库按视频的“模型 → 命令 → 执行 → 反馈”原理独立实现，**不是视频源码的逐行转录**。B 站直连受 412 风控限制，未取得作者原始代码；来源及差异见 [视频对应说明](docs/video_mapping.md)。

## 功能

- 调用百炼**已发布的 Agent 1.0 应用**，使用 `dashscope.Application.call`，不是普通模型的聊天接口。
- Streamlit 流式聊天、多轮 `session_id`、新对话、配置重载与对话导出。
- 本地工具模式：模型逐轮选择列目录、读写文件、打包 ZIP，观察执行结果并继续。
- 默认关闭 shell；可显式开启，复现视频中的命令执行思路。
- 包含精简 CLI、系统提示词、云端发布步骤、设计分析和离线自动测试。

## 启动（Python 3.12）

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
# 在本地编辑 .env，填入真实的 DASHSCOPE_API_KEY 和 BAILIAN_APP_ID
.venv/Scripts/python.exe -m streamlit run app.py --server.address 127.0.0.1
```

打开 [本地网页](http://localhost:8501)。Windows 也可以运行 `./scripts/start.ps1`。
没有配置 Key 和应用 ID 时，网页可以启动，但会禁用聊天；不会用模拟回复冒充百炼调用成功。

## 云端准备

按 [创建与发布指南](docs/bailian_setup.md) 在**百炼旧版控制台**创建 Agent 1.0，粘贴 [系统提示词](prompts/flowagent_system.md)，选择模型并发布，再配置 `.env`。

本实现针对北京地域的 DashScope 旧版应用接口。Key、应用与工作空间应匹配；子空间可配置 `BAILIAN_WORKSPACE_ID`。不要填阿里云 AccessKey，也不要将 Key 提交到 GitHub。

## 实验

在网页选择“本地工具循环”，输入：

> 请先查看工作目录，然后创建 hello.txt，内容为“你好，Agent”，读取验证并打包成 hello.zip。

页面会展示动作与工具观察，真实产物位于 `workspace/`。也可运行：

```powershell
.venv/Scripts/python.exe mini_agent.py "创建 hello.txt，读取验证并打包成 hello.zip"
# 只有需要视频中的任意命令执行时才启用 shell：
.venv/Scripts/python.exe mini_agent.py "用 shell 打印当前目录" --allow-shell
```

文件工具限制在 `workspace/`；**shell 并不受该路径限制**，它拥有当前用户权限，仅 cwd 设在该目录。命令执行超时 30 秒、循环最多 8 轮（网页可调整）。工具失败时观察会返回模型；不会自动重试整个任务，以免重复写入。

## 验证

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-dev.txt
.venv/Scripts/python.exe -m pytest -q
# 配置真实应用后执行云端两轮验证（会调用百炼）：
.venv/Scripts/python.exe -m scripts.smoke_cloud
```

离线测试使用脚本化响应验证实际文件、ZIP、循环退出、错误纠正、路径限制、会话复用和 Streamlit 界面；它们**不能证明云端应用已创建、已发布或已联通**。实际进展记录见 [交付状态](docs/status.md)。

## 设计思想

符合 **LLM + 上下文 + 工具**、模型决策与执行器分离，以及 **动作—观察闭环**；运行层提供步数限制、格式验证和错误反馈。普通对话模式仅调用云端应用；本地工具模式才在用户电脑上形成完整工具循环。详见 [设计分析及 ai-agent-book 章节映射](docs/design.md)。

## 文件

| 文件 | 用途 |
|---|---|
| `app.py` | Streamlit 网页 |
| `bailian_client.py` | 流式应用调用和会话管理 |
| `local_agent.py` | 工具执行、反馈和循环控制 |
| `mini_agent.py` | 视频原理的精简 CLI |
| `prompts/flowagent_system.md` | 百炼应用系统提示词 |
| `docs/` | 发布、设计、视频映射和状态 |
| `tests/` | 离线自动验证 |

原创实现采用 MIT 许可。参考书和视频版权归各自作者所有；本仓库不分发视频或复制书籍全文。
