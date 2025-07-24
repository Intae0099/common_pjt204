import { http, HttpResponse } from 'msw'

export const handlers = [
  http.post('/api/ai-consult', () => {
    return HttpResponse.json({
      result: '상담 요청이 정상적으로 처리되었습니다.',
      nextAction: '판례 예측 요청 가능',
    })
  }),

  http.post('/api/verdict/predict', async ({ request }) => {
    const body = await request.json()
    console.log('판례 예측 요청:', body)
    return HttpResponse.json({
      verdictSummary: '유사 판례 분석 결과: 위자료 청구 가능성이 높습니다.',
      confidence: 0.91,
      lawyers: [
        {
          id: 1,
          name: '김지훈 변호사',
          specialty: '형사 사건',
          intro: '피해자와 피의자 모두의 입장을 이해하며 조력하는 변호사입니다.',
          image: 'https://via.placeholder.com/80x80'
        },
        {
          id: 2,
          name: '이은지 변호사',
          specialty: '이혼·가사',
          intro: '가정법 분야에서 15년 경력의 전문가입니다.',
          image: 'https://via.placeholder.com/80x80'
        }
      ]
    })
  }),

  http.get('/api/lawyers/:id', ({ params }) => {
    const { id } = params
    return HttpResponse.json({
      id,
      name: id === '1' ? '홍길동' : '이몽룡',
      field: id === '1' ? '형사' : '민사',
      experience: '10년 이상',
      rating: 4.8,
    })
  }),

]
