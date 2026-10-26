"""北京地域 Agent 1.0 / FlowAgent 的 DashScope 应用调用。"""
from dataclasses import dataclass, field
from http import HTTPStatus
import os

import dashscope
from dashscope import Application
from dotenv import dotenv_values


class BailianError(RuntimeError):
    pass


@dataclass
class BailianClient:
    api_key: str = field(repr=False)
    app_id: str
    workspace_id: str = ""
    session_id: str = ""

    @classmethod
    def from_env(cls):
        # 不把 .env 写入进程环境，允许网页在文件修改后重新加载。
        config = dotenv_values(".env")
        def value(name):
            return (os.getenv(name) or config.get(name) or "").strip()
        return cls(value("DASHSCOPE_API_KEY"), value("BAILIAN_APP_ID"),
                   value("BAILIAN_WORKSPACE_ID"))

    @property
    def ready(self):
        return bool(self.api_key and self.app_id)

    def reset(self):
        self.session_id = ""

    def stream(self, prompt):
        if not self.ready:
            raise BailianError("请先在 .env 中配置 DASHSCOPE_API_KEY 和 BAILIAN_APP_ID。")
        dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
        kwargs = dict(api_key=self.api_key, app_id=self.app_id, prompt=prompt,
                      stream=True, incremental_output=True)
        if self.session_id:
            kwargs["session_id"] = self.session_id
        if self.workspace_id:
            kwargs["workspace"] = self.workspace_id
        received = False
        try:
            for response in Application.call(**kwargs):
                if response.status_code != HTTPStatus.OK:
                    code = str(response.get("code", response.status_code))
                    request_id = str(response.get("request_id", ""))
                    # 服务端 message 可能回显用户数据；界面仅显示错误码和请求 ID。
                    raise BailianError(f"百炼调用失败：{code}；request_id={request_id}。"
                                       "请检查地域、应用发布状态、Key 权限；会话失效时开始新对话。")
                output = response.get("output") or {}
                self.session_id = output.get("session_id") or self.session_id
                text = output.get("text") or ""
                if text:
                    received = True
                    yield text
        except BailianError:
            raise
        except Exception:
            raise BailianError("连接百炼失败，请检查网络与应用配置后重试。") from None
        if not received:
            raise BailianError("百炼未返回文本，请检查已发布应用的输出配置。")

    def complete(self, prompt):
        return "".join(self.stream(prompt))
