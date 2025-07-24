# ai/tests/conftest.py
import sys
import os

# 이 파일(ai/tests/conftest.py) 기준으로 두 단계 위가 프로젝트 루트라고 가정
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)