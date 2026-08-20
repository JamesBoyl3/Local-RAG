
import pytest
from utils.mock import Mock

from localrag import LLM
from localrag.core import LLMConfig


def test_get_answer_() -> None: 
    config = LLMConfig(TEMP=0.5, MAX_TOKENS=100)
    llm = LLM(host="localhost", port=8080, config=config)

    fake_response = Mock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {"choices": [{"message": {"content": "abc"}}]}
    llm._session.post = Mock(return_value=fake_response)

    conversation = [{"role": "user", "content": "hello"}]
    answer = llm.get_answer(conversation)

    assert answer == "abc"
    llm._session.post.assert_called_once_with(
        "http://localhost:8080/v1/chat/completions",
        json={
            "messages": conversation,
            "temperature": 0.5,
            "max_tokens": 100,
        },
        timeout=120,
    )

def test_get_answer_errors() -> None: 
	config = LLMConfig()
	llm = LLM(host="localhost", port="8080", config=config)

	fake_response = Mock()
	fake_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
	llm._session.post = Mock(return_value=fake_response)

	with pytest.raises(requests.HTTPError):
		llm.get_answer([{"role": "user", "content": "hello"}])
