import unittest
from unittest.mock import patch, MagicMock
import tenacity

# ai/config/.env에서 GMS_KEY와 GMS_BASE_URL을 로드하므로,
# client 객체는 이미 초기화된 상태입니다.
from llm.openai_client import call_gpt4o

class TestOpenAIClient(unittest.TestCase):

    @patch('llm.openai_client.client.chat.completions.create')
    def test_call_gpt4o_success(self, mock_create):
        """call_gpt4o 함수가 성공적으로 API 응답을 처리하는지 테스트"""
        # Mock response 설정
        mock_response = MagicMock()
        mock_msg = MagicMock()
        mock_msg.content = "테스트 응답"
        mock_choice = MagicMock()
        mock_choice.message = mock_msg
        mock_response.choices = [mock_choice]
        mock_create.return_value = mock_response

        messages = [{"role": "user", "content": "테스트"}]
        response = call_gpt4o(messages)

        self.assertEqual(response, "테스트 응답")
        mock_create.assert_called_once_with(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.3,
            max_tokens=2048
        )

    @patch('llm.openai_client.client.chat.completions.create')
    def test_call_gpt4o_api_error(self, mock_create):
        """재시도 후 최종적으로 tenacity.RetryError를 발생시키는지 테스트"""
        # API 호출 시 예외를 발생시키도록 설정
        mock_create.side_effect = Exception("API 통신 오류")

        with self.assertRaises(tenacity.RetryError):
            # 내부에서 3회 재시도 후 RetryError 발생
            call_gpt4o([{"role": "user", "content": "테스트"}])

if __name__ == '__main__':
    unittest.main()
