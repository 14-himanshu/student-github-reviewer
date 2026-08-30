from unittest.mock import patch, MagicMock
from agent.nodes import _is_rate_limit_error

def test_is_rate_limit_error():
    assert _is_rate_limit_error(Exception("429 Too Many Requests")) is True
    assert _is_rate_limit_error(Exception("rate limit exceeded")) is True
    assert _is_rate_limit_error(Exception("Connection timeout")) is False

@patch("agent.nodes.llm")
def test_invoke_llm_with_retry_success(mock_llm):
    from agent.nodes import _invoke_llm_with_retry
    from langchain_core.messages import HumanMessage
    
    mock_llm.invoke.return_value = MagicMock(content="Success!")
    response = _invoke_llm_with_retry([HumanMessage(content="Test")])
    assert response.content == "Success!"
    mock_llm.invoke.assert_called_once()
