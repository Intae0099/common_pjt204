// src/mocks/handlers.js
import { rest } from 'msw'

export const handlers = [
  // 예시: AI 사전상담 요청
  rest.post('/api/ai-consult', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        result: '상담 요청이 정상적으로 처리되었습니다.',
        nextAction: '판례 예측 요청 가능',
      })
    )
  }),

  // 예시: 추천 변호사 리스트
  rest.get('/api/lawyers/recommend', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { id: 1, name: '홍길동', field: '형사' },
        { id: 2, name: '이몽룡', field: '민사' },
      ])
    )
  }),
]
