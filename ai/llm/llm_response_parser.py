import re
import json
from typing import Dict, Any, List
from langchain.schema import BaseOutputParser
# from pydantic import BaseModel, Field # CaseAnalysisResult 이동으로 더 이상 필요 없음

from app.api.schemas.analysis import CaseAnalysisResult # 새 위치에서 임포트

class CotOutputParser(BaseOutputParser):
    def parse(self, text: str) -> Dict[str, Any]:
        text = text.strip()
        # JSON 블록이면 그대로 thought/conclusion 모두 raw로 남김
        if text.startswith("{\n"):
            return {"thought_process": text, "conclusion": text}

        # "결론:" 헤더 기준 분리
        match = re.search(r"결론:\s*(.*)", text, re.DOTALL)
        if match:
            conclusion = match.group(1).strip()
            thought    = text[:match.start()].strip()
        else:
            conclusion = ""
            thought    = text

        return {"thought_process": thought, "conclusion": conclusion}


def parse_case_analysis_output(raw: str) -> CaseAnalysisResult:
    raw = raw.strip()

    # 1) JSON 형태 처리 우선
    if raw.startswith("{\n"):
        payload = json.loads(raw)
        report  = payload.get("data", {}).get("report", {})

        # Process statutes to handle 'article' (singular) to 'articles' (plural) conversion
        processed_statutes = []
        raw_statutes_from_llm = payload.get("statutes", [])
        for s_data in raw_statutes_from_llm:
            if isinstance(s_data, dict):
                code = s_data.get("code", "")
                articles = s_data.get("articles", [])
                if not isinstance(articles, list):
                    articles = [articles] if articles is not None else []
                
                # If 'articles' is empty, but 'article' (singular) exists, use it
                if not articles and s_data.get("article"):
                    article_singular = s_data.get("article")
                    if isinstance(article_singular, str):
                        articles = [article_singular]
                    elif isinstance(article_singular, list): # Defensive: if LLM sends list for singular
                        articles = article_singular
                
                processed_statutes.append({"code": code, "articles": articles})
            # Handle cases where LLM might return a string directly (less likely with new prompt)
            elif isinstance(s_data, str):
                # Attempt to parse simple string like "형법 347조"
                match = re.match(r"(.+?)\s*(\d+조.*)", s_data)
                if match:
                    code = match.group(1).strip()
                    articles = [match.group(2).strip()]
                else:
                    code = s_data.strip()
                    articles = []
                processed_statutes.append({"code": code, "articles": articles})

        return CaseAnalysisResult(
            issues             = report.get("issues", []),
            opinion            = report.get("opinion", ""),
            expected_sentence  = report.get("sentencePrediction", ""),
            confidence         = report.get("confidence", 0.0),
            references         = report.get("references", {}),
            statutes           = processed_statutes, # Use the processed list
            tags               = payload.get("tags", []),
            recommendedLawyers = payload.get("recommendedLawyers", [])
        )

    # 2) 텍스트 포맷 파싱
    issues            = []
    opinion           = ""
    expected_sentence = ""
    confidence        = 0.0

    # ———— 쟁점 추출 ————
    # "쟁점:" 이후 빈 줄(또는 다음 헤더) 전까지 모두 가져오기
    issues_block = re.search(
        r"쟁점:\s*([\s\S]*?)(?=\n\s*\n|소견:|예상 형량:|신뢰도:|\Z)",
        raw
    )
    if issues_block:
        lines = issues_block.group(1).splitlines()
        cleaned = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # "1. ", "- ", "* " 등 제거
            item = re.sub(r"^(?:\d+\.\s*|[\-\*]\s*)", "", line).strip()
            if item:
                cleaned.append(item)
        issues = cleaned

    # ———— 소견 추출 ————
    opinion_match = re.search(
        r"소견:\s*([\s\S]*?)(?=\n\s*\n|쟁점:|예상 형량:|신뢰도:|\Z)",
        raw
    )
    if opinion_match:
        opinion = opinion_match.group(1).strip()

    # ———— 예상 형량 추출 ————
    sent_match = re.search(
        r"예상 형량:\s*([\s\S]*?)(?=\n\s*\n|쟁점:|소견:|신뢰도:|\Z)",
        raw
    )
    if sent_match:
        expected_sentence = sent_match.group(1).strip()

    # ———— 신뢰도 추출 ————
    conf_match = re.search(r"신뢰도:\s*([0-9.]+)", raw)
    if conf_match:
        try:
            confidence = float(conf_match.group(1))
        except ValueError:
            confidence = 0.0

    return CaseAnalysisResult(
        issues             = issues,
        opinion            = opinion,
        expected_sentence  = expected_sentence,
        confidence         = confidence,
        references         = {},
        statutes           = [],  # 텍스트 형태에서는 기본값으로 빈 리스트
        tags               = [],
        recommendedLawyers = []
    )