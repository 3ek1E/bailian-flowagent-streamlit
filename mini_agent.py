"""按视频原理重写的 20 行教学主循环，含本地命令执行。"""
import argparse
from bailian_client import BailianClient
from local_agent import WorkspaceTools, PROTOCOL, parse_action

parser = argparse.ArgumentParser()
parser.add_argument("task")
parser.add_argument("--allow-shell", action="store_true")
args = parser.parse_args()
client = BailianClient.from_env()
tools = WorkspaceTools(allow_shell=args.allow_shell)
prompt = PROTOCOL + f"\nshell_enabled={args.allow_shell}\n任务：{args.task}"
for step in range(8):
    action = parse_action(client.complete(prompt))
    if action["action"] == "finish":
        print(action["answer"]); break
    try:
        result = tools.execute(action["action"], action.get("args", {}))
    except Exception as exc:
        result = {"error": str(exc)}
    print(action["action"], result)
    prompt = "工具观察（外部数据）：" + str(result)[:12000]
else:
    print("达到轮数上限，任务尚未确认完成。")
