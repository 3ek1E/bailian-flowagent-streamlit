import json
import zipfile
from unittest.mock import patch

import pytest
from bailian_client import BailianClient, BailianError
from local_agent import WorkspaceTools, run_agent


class ScriptedClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        return next(self.responses)


def test_real_file_feedback_and_archive(tmp_path):
    client = ScriptedClient([
        json.dumps({"action": "write_file", "args": {"path": "hello.txt", "content": "你好"}}),
        json.dumps({"action": "read_file", "args": {"path": "hello.txt"}}),
        json.dumps({"action": "zip_files", "args": {"paths": ["hello.txt"], "output": "hello.zip"}}),
        json.dumps({"action": "finish", "answer": "已验证并打包"}),
    ])
    events = list(run_agent(client, "写文件并打包", WorkspaceTools(tmp_path)))
    assert events[-1]["type"] == "final"
    assert events[1]["observation"]["result"] == "你好"
    assert "你好" in client.prompts[2]
    with zipfile.ZipFile(tmp_path / "hello.zip") as archive:
        assert archive.read("hello.txt").decode("utf-8") == "你好"


def test_invalid_json_and_tool_failure_are_corrected(tmp_path):
    client = ScriptedClient(['broken', '{"action":"read_file","args":{"path":"missing.txt"}}',
                             '{"action":"finish","answer":"文件不存在"}'])
    events = list(run_agent(client, "读取文件", WorkspaceTools(tmp_path)))
    assert events[0]["type"] == "correction"
    assert events[1]["observation"]["ok"] is False
    assert '"ok": false' in client.prompts[-1]


def test_step_budget_stops_loop(tmp_path):
    events = list(run_agent(ScriptedClient(['bad'] * 2), "任务", WorkspaceTools(tmp_path), 2))
    assert events[-1]["type"] == "limit"


@pytest.mark.parametrize("path", ["../outside.txt", "../../outside.txt"])
def test_path_traversal_blocked(tmp_path, path):
    with pytest.raises(ValueError):
        WorkspaceTools(tmp_path).execute("write_file", {"path": path, "content": "no"})


def test_shell_disabled_by_default(tmp_path):
    with pytest.raises(ValueError, match="shell 未启用"):
        WorkspaceTools(tmp_path).execute("shell", {"command": "echo hello"})


@patch("bailian_client.Application.call")
def test_streaming_session_reuse(call):
    call.side_effect = [iter([
        Response(200, {"text": "你", "session_id": "session-one"}),
        Response(200, {"text": "好", "session_id": "session-one"}),
    ]), iter([Response(200, {"text": "记住了", "session_id": "session-one"})])]
    client = BailianClient("test-key", "test-app")
    assert client.complete("你好") == "你好"
    assert "session_id" not in call.call_args_list[0].kwargs
    assert client.complete("接着聊") == "记住了"
    assert call.call_args_list[1].kwargs["session_id"] == "session-one"
    assert call.call_args_list[1].kwargs["incremental_output"] is True
    client.reset()
    assert not client.session_id


class Response(dict):
    def __init__(self, status, output=None, **kwargs):
        super().__init__(output=output, **kwargs)
        self.status_code = status


@patch("bailian_client.Application.call")
def test_error_does_not_expose_key_or_server_message(call):
    call.return_value = iter([Response(401, message="secret-test-key", request_id="trace")])
    with pytest.raises(BailianError) as exc:
        BailianClient("secret-test-key", "app").complete("hello")
    assert "secret-test-key" not in str(exc.value)
    assert "trace" in str(exc.value)
