from streamlit.testing.v1 import AppTest
from bailian_client import BailianClient
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_unconfigured_ui(monkeypatch):
    monkeypatch.setattr(BailianClient, "from_env", classmethod(lambda cls: cls("", "")))
    app = AppTest.from_file(APP).run()
    assert not app.exception
    assert app.chat_input[0].disabled


def test_chat_and_mode_reset(monkeypatch):
    monkeypatch.setattr(BailianClient, "from_env", classmethod(lambda cls: cls("fake", "app")))
    monkeypatch.setattr(BailianClient, "stream", lambda self, prompt: iter(["你好", "，世界"]))
    app = AppTest.from_file(APP).run()
    app.chat_input[0].set_value("你好").run()
    assert not app.exception
    assert app.session_state["messages"][-1]["content"] == "你好，世界"
    app.radio[0].set_value("本地工具循环").run()
    assert not app.exception
    assert not app.session_state["messages"]
