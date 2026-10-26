"""从项目根目录运行 python -m scripts.smoke_cloud；会实际调用百炼。"""
import json
from bailian_client import BailianClient

client = BailianClient.from_env()
print(client.complete("请记住口令：小龙虾实验。只回复已记住。"))
print(client.complete("我刚才让你记住的口令是什么？"))
print(json.dumps({"has_session_id": bool(client.session_id)}, ensure_ascii=False))
