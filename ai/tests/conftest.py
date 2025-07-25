# ai/tests/conftest.py
import sys
from pathlib import Path

# 현재 파일 위치(ai/tests/conftest.py)의 부모(=ai) 폴더를 루트로 잡는다
AI_ROOT = str(Path(__file__).resolve().parent.parent)
if AI_ROOT not in sys.path:
    sys.path.insert(0, AI_ROOT)
