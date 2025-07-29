import json
import logging
import re

# 로거 설정
logger = logging.getLogger(__name__)

class StructuringParser:
    """
    LLM의 원시 출력을 안전하게 JSON 파싱하고, 특정 키(title, summary, fullText)를 보장하는 파서.
    비정상/깨진 JSON에도 대응하며, 보정 발생 시 WARNING 로그를 남깁니다.
    """

    SUMMARY_MAX_LEN = 200  # 요약 최대 길이
    DEFAULT_TITLE = "사건 제목 미정(자동생성)"

    def parse(self, raw_llm_output: str) -> dict:
        """
        LLM의 원시 문자열 출력을 파싱하여 표준화된 딕셔너리(title, summary, fullText)를 반환합니다.
        JSON 파싱 실패 시 복구 로직을 적용하고, 필수 키가 누락되면 보정합니다.
        """
        parsed_data = {}
        trimmed_raw_output = self._trim_whitespace(raw_llm_output)

        try:
            # 표준 JSON 파싱 시도
            parsed_data = json.loads(trimmed_raw_output)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 실패: {e}. 복구 모드 진입. 원시 출력: '{trimmed_raw_output[:100]}...' ")
            # 1) 닫힘 중괄호가 있는 경우: 느슨한 정규식으로 키/값 추출(개행 포함)
            # 2) 닫힘 중괄호가 없거나 명백히 잘린 경우: 원문 전체를 fullText로 사용
            s = trimmed_raw_output.strip()
            if s.startswith("{") and s.endswith("}"):
                soft = self._extract_loose_json(s)
                parsed_data = soft if soft else {"fullText": trimmed_raw_output}
            else:
                parsed_data = {"fullText": trimmed_raw_output}

        # 결과 딕셔너리 초기화
        result = {
            "title": self._trim_whitespace(parsed_data.get("title", "")),
            "summary": self._trim_whitespace(parsed_data.get("summary", "")),
            "fullText": self._trim_whitespace(parsed_data.get("fullText", "")),
        }

        # fullText 보정: content/text/body 같은 대체 키 허용
        if not result["fullText"]:
            for k in ("content", "text", "body"):
                v = parsed_data.get(k)
                if isinstance(v, str) and v.strip():
                    result["fullText"] = self._trim_whitespace(v)
                    break
            if not result["fullText"]:
                result["fullText"] = trimmed_raw_output
                logger.warning("'fullText' 키 누락 또는 비어있음. 원시 출력을 'fullText'로 사용합니다.")

        # summary 보정
        if not result["summary"]:
            if result["fullText"]:
                result["summary"] = self._trim_whitespace(result["fullText"])[:self.SUMMARY_MAX_LEN]
                logger.warning(f"'summary' 키 누락 또는 비어있음. 'fullText'에서 요약 생성 (최대 {self.SUMMARY_MAX_LEN}자).")
            else:
                result["summary"] = ""
                logger.warning(f"'summary' 키 누락 또는 비어있음. 'fullText'도 없어 요약 생성 불가.")

        # title 보정 (첫 문장 보존: 마침표/물음표/느낌표 등 포함하여 잘라냄)
        if not result["title"]:
            if result["summary"]:
                result["title"] = self._first_sentence(result["summary"]) or self.DEFAULT_TITLE
                logger.warning(f"'title' 키 누락 또는 비어있음. 'summary'에서 제목 생성.")
            elif result["fullText"]:
                result["title"] = self._first_sentence(result["fullText"]) or self.DEFAULT_TITLE
                logger.warning(f"'title' 키 누락 또는 비어있음. 'fullText'에서 제목 생성.")
            else:
                result["title"] = self.DEFAULT_TITLE
                logger.warning(f"'title' 키 누락 또는 비어있음. 기본 제목 '{self.DEFAULT_TITLE}'으로 설정.")

        # 최종 길이/트리밍 적용
        result["title"] = self._trim_whitespace(result["title"])
        result["summary"] = self._trim_whitespace(result["summary"])[:self.SUMMARY_MAX_LEN]
        result["fullText"] = self._trim_whitespace(result["fullText"])

        # 모든 키가 비었을 때 방어적 보정
        if not result["title"] and not result["summary"] and not result["fullText"]:
            result["fullText"] = trimmed_raw_output
            result["summary"] = trimmed_raw_output[:self.SUMMARY_MAX_LEN] if trimmed_raw_output else ""
            result["title"] = self._first_sentence(trimmed_raw_output) or self.DEFAULT_TITLE
            logger.warning("모든 필수 키가 비어있어 원시 출력을 기반으로 최종 보정 수행.")

        return result

    def _extract_loose_json(self, text: str) -> dict:
        """
        따옴표 안 개행 등으로 JSON 표준 파싱이 실패할 때, 정규식으로 핵심 키를 느슨하게 추출.
        """
        data = {}
        for key in ("title", "summary", "fullText", "content", "text", "body"):
            m = re.search(rf'"{key}"\s*:\s*"(.*?)"', text, flags=re.DOTALL)
            if m:
                # 내부 이스케이프 간단 처리 및 트리밍
                val = m.group(1).replace('\\"', '"')
                data[key] = self._trim_whitespace(val)
        return data

    def _first_sentence(self, text: str) -> str:
        """
        첫 문장을 종결부호(., !, ?, 일본/중국어 마침표 포함)까지 포함하여 추출.
        종결부호가 없으면 전체 문자열을 반환.
        """
        if not isinstance(text, str):
            return ""
        s = text.strip()
        if not s:
            return ""
        m = re.match(r'(.+?[\.!?。．？！])', s, flags=re.DOTALL)
        return (m.group(1).strip() if m else s)

    def _trim_whitespace(self, text: str) -> str:
        """
        문자열의 앞뒤 공백/개행 정리:
        - 각 라인의 앞뒤 공백 제거
        - 빈 라인 제거
        - 남은 라인들을 개행으로 다시 결합 후 전체 트리밍
        """
        if not isinstance(text, str):
            return ""
        cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
        return '\n'.join(cleaned_lines).strip()
