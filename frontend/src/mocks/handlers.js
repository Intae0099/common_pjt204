// src/mocks/handlers.js

// 1. 'rest' 대신 'http'와 'HttpResponse'를 import 합니다.
import { http, HttpResponse } from 'msw'

export const handlers = [
  // 2. 'rest.post'를 'http.post'로 변경합니다.
  // 3. 콜백 함수의 인자(req, res, ctx) 구조가 단순화되고, 응답은 HttpResponse를 사용합니다.
  http.post('/api/ai-consult', () => {
    return HttpResponse.json({
        result: '상담 요청이 정상적으로 처리되었습니다.',
        nextAction: '판례 예측 요청 가능',
      }
      // status는 기본 200이므로 생략 가능합니다.
      // { status: 200 }
    )
  }),

  // 'rest.get'을 'http.get'으로 변경합니다.
  http.get('/api/lawyers/recommend', () => {
    return HttpResponse.json([
      { id: 1, name: '홍길동', field: '형사' },
      { id: 2, name: '이몽룡', field: '민사' },
    ])
  }),
]
