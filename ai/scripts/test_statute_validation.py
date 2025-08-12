#!/usr/bin/env python3
"""
법령 검증 시스템 테스트 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.statute_validation_service import StatuteValidationService

def test_basic_validation():
    """기본 법령 검증 테스트"""
    print("=== 기본 법령 검증 테스트 ===")
    
    service = StatuteValidationService()
    
    test_cases = [
        "형법 제347조(사기)",
        "민법 제750조(불법행위)", 
        "형사법 제123조",  # 존재하지 않는 법령
        "형볍 제347조",    # 오타
        "민법, 상법",      # 조항 없음
        "형법 제347조, 민법 제750조, 존재하지않는법 제999조"
    ]
    
    for test_case in test_cases:
        print(f"\n--- 테스트: {test_case} ---")
        try:
            results = service.validate_statutes(test_case)
            
            for result in results:
                print(f"원본: {result.original_text}")
                print(f"결과: {result.validation_result}")
                if result.matched_statute_id:
                    print(f"매칭: {result.statute_name}")
                    print(f"부처: {result.department}")
                print(f"신뢰도: {result.confidence_score:.3f}")
                if result.error_type:
                    print(f"오류유형: {result.error_type}")
                print("---")
                
        except Exception as e:
            print(f"오류: {e}")

def test_enhancement():
    """법령 정보 보강 테스트"""
    print("\n=== 법령 정보 보강 테스트 ===")
    
    service = StatuteValidationService()
    
    test_statute = "형법 제347조(사기), 민법 제750조"
    
    print(f"입력: {test_statute}")
    
    try:
        # 검증
        validation_results = service.validate_statutes(test_statute)
        
        # 원본 정보 (조항 포함)
        original_statutes = [
            {"code": "형법", "article": "제347조(사기)"},
            {"code": "민법", "article": "제750조"}
        ]
        
        # 보강
        enhanced = service.enhance_statutes_response(validation_results, original_statutes)
        
        print("\n보강된 결과:")
        for statute in enhanced:
            print(f"- 법령: {statute.code}")
            print(f"  조항: {statute.articles}")
            print(f"  설명: {statute.description}")
            print(f"  ID: {statute.statute_id}")
            print(f"  부처: {statute.department}")
            print(f"  신뢰도: {statute.confidence:.3f}")
            print()
            
    except Exception as e:
        print(f"오류: {e}")


def main():
    """메인 테스트 함수"""
    print("법령 검증 시스템 테스트 시작\n")
    
    try:
        test_basic_validation()
        test_enhancement()
        
        print("\n=== 테스트 완료 ===")
        
    except KeyboardInterrupt:
        print("\n테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    main()