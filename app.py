from pathlib import Path
import json
import streamlit as st

from bailian_client import BailianClient, BailianError
from local_agent import WorkspaceTools, run_agent

st.set_page_config(page_title="FlowAgent · 小龙虾实验室", page_icon="🦞", layout="wide")
st.title("🦞 小龙虾实验室")
st.caption("阿里云百炼 Agent 1.0 · Streamlit · 模型决策与本地工具循环")

if "client" not in st.session_state:
    st.session_state.client = BailianClient.from_env()
if "messages" not in st.session_state:
    st.session_state.messages = []
client = st.session_state.client

with st.sidebar:
    st.subheader("对话设置")
    mode = st.radio("运行模式", ["百炼对话", "本地工具循环"])
    if st.session_state.get("last_mode", mode) != mode:
        client.reset()
        st.session_state.messages = []
    st.session_state.last_mode = mode
    st.success("百炼配置已加载") if client.ready else st.info("等待 .env 配置")
    if st.button("重新加载配置 / 新对话", use_container_width=True):
        st.session_state.client = BailianClient.from_env()
        st.session_state.messages = []
        st.rerun()
    steps = st.slider("工具循环轮数上限", 1, 15, 8)
    allow_shell = st.checkbox("启用 shell 命令（默认关闭）", value=False)
    if allow_shell:
        st.warning("shell 具备当前用户的系统权限，工作目录不是沙箱。仅对可信任务启用。")
    st.caption("文件工具工作目录：" + str(Path("workspace").resolve()))
    st.download_button("导出对话", json.dumps(st.session_state.messages, ensure_ascii=False, indent=2),
                       file_name="conversation.json", mime="application/json")

with st.expander("快速开始与实验任务", expanded=not client.ready):
    st.markdown("在百炼旧版控制台创建 **Agent 1.0**，粘贴 `prompts/flowagent_system.md`，发布后"
                "将应用 ID 与 API Key 填入本地 `.env`，再点击「重新加载配置 / 新对话」。")
    st.code("请先查看工作目录，然后创建 hello.txt，内容为‘你好，Agent’，读取验证并打包成 hello.zip。", language=None)
    st.caption("普通对话展示流式回复；工具模式展示动作和真实执行结果。未配置时不会模拟云端成功。")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        for event in message.get("events", []):
            with st.expander(f"第 {event.get('step', '?')} 轮 · {event.get('action', event['type'])}"):
                st.json(event)

if prompt := st.chat_input("输入问题，或让 Agent 操作 workspace 中的文件", disabled=not client.ready):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        events = []
        answer = ""
        try:
            if mode == "百炼对话":
                answer = st.write_stream(client.stream(prompt))
            else:
                tools = WorkspaceTools(allow_shell=allow_shell)
                for event in run_agent(client, prompt, tools, steps):
                    if event["type"] in ("final", "limit"):
                        answer = event["text"]
                        st.markdown(answer)
                    else:
                        events.append(event)
                        with st.expander(f"第 {event['step']} 轮 · {event.get('action', '格式纠正')}", expanded=True):
                            st.json(event)
        except BailianError as exc:
            answer = str(exc) + " 本轮可能未完成，请核对文件结果后重试。"
            st.error(answer)
            client.reset()
        st.session_state.messages.append({"role": "assistant", "content": answer, "events": events})
