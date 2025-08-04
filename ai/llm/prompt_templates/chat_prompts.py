from typing import List, Dict, Deque, Tuple

# 시스템 프롬프트를 상수로 정의하여 일관성 유지
SYSTEM_PROMPT = '''당신은 한국법에 대한 풍부한 지식과 경험을 가진 법률 전문가 AI 어시스턴트입니다.
사용자가 헌법·민법·형법·상법 등을 포함한 한국 법률 관련 질문을 하면, 반드시 정확한 법 조문과 해설을 바탕으로 친절하고 명확하게 답변해주세요.
질문의 주제가 한국 법률이 아닌 경우나 법률 자문을 제공할 수 없는 상황에는 "죄송합니다. 저는 법률 상담만을 제공하도록 설계되었습니다." 라고 간결히 안내해주세요.
'''  

class ChatPromptTemplate:
    """채팅 프롬프트를 생성하는 클래스"""

    @staticmethod
    def build_messages(history: Deque[Tuple[str, str]], new_message: str) -> List[Dict[str, str]]:
        """
        대화 이력과 새로운 메시지를 바탕으로 LLM에 전달할 messages 리스트를 생성합니다.
        """
        messages: List[Dict[str, str]] = []
        # 시스템 프롬프트 삽입
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
        # 과거 대화 이력 반영
        for role, content in history:
            messages.append({"role": role, "content": content})
        # 사용자 메시지 추가
        messages.append({"role": "user", "content": new_message})
        return messages
