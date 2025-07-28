import { http, HttpResponse } from 'msw'

export const handlers = [
  http.post('/api/auth/lawyers/login', async ({ request }) => {
    const body = await request.json()
    const { loginId, loginPwd } = body

    // 원하는 가짜 조건 추가 가능
    if (loginId === 'wjddusdl921@gmail.com' && loginPwd === '0123456') {
      return HttpResponse.json({
        access_token: 'fake-jwt-token-for-test'
      })
    } else {
      return HttpResponse.json(
        { detail: '이메일 또는 비밀번호가 올바르지 않습니다.' },
        { status: 401 }
      )
    }
  }),
  // ✅ 변호사 본인 정보
  http.get('/api/lawyers/me', () => {
    return HttpResponse.json({
      name: '김지훈',
      loginEmail: 'lawyer@example.com',
      introduction: '형사/민사 사건을 다루는 10년차 변호사입니다.',
      tags: ['형사', '이혼', '가사'],
    })
  }),

  // ✅ 상담 예약 목록 (오늘 이후를 테스트하기 위해 미래 날짜 포함)
  http.get('/api/appointments/me', () => {
    return HttpResponse.json([
      {
        appointmentId: 101,
        clientId: 1,
        startTime: new Date(Date.now() + 3 * 60 * 60 * 1000).toISOString() // 3시간 뒤
      },
      {
        appointmentId: 102,
        clientId: 2,
        startTime: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 내일
      }
    ])
  }),

  // ✅ 클라이언트 목록
  http.get('/api/admin/clients/list', () => {
    return HttpResponse.json([
      {
        clientId: 1,
        name: '홍길동',
        email: 'client1@example.com'
      },
      {
        clientId: 2,
        name: '이몽룡',
        email: 'client2@example.com'
      }
    ])
  }),

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
  // 변호사 목록 조회
  http.get('/api/admin/lawyers/list', () => {
    return HttpResponse.json([
      {
        id: 1,
        name: '이정연',
        tags: ['교통사고', '합의'],
        profile_image: 'https://via.placeholder.com/150',
        introduction: '교통사고 전문 변호사입니다.'
      },
      {
        id: 2,
        name: '윤규성',
        tags: ['이혼', '합의'],
        profile_image: 'https://via.placeholder.com/150',
        introduction: '합의 경험이 풍부한 변호사입니다.'
      },
      {
        id: 3,
        name: '전해지',
        tags: ['교통사고', '합의'],
        profile_image: 'https://via.placeholder.com/150',
        introduction: '의뢰인의 입장에서 최선을 다하겠습니다.'
      }
    ])
  }),

  // 특정 날짜에 변호사 예약 불가 시간 조회
  http.get('/api/lawyers/:lawyerId/unavailable-slot', ({ request }) => {
    const url = new URL(request.url)
    const date = url.searchParams.get('date')

    const unavailable = {
      '2025-07-25': ['10:00', '14:30'],
      '2025-07-26': ['09:00', '11:00']
    }

    return HttpResponse.json(unavailable[date] || [])
  }),


  // 나의 상담신청서 목록
  http.get('/api/applications/me', () => {
    return HttpResponse.json([
      {
        id: 101,
        title: '7월 교통사고 사건 신청서'
      },
      {
        id: 102,
        title: '합의 관련 상담 신청서'
      }
    ])
  }),

  // 상담 예약 요청
  http.post('/api/appointments', async ({ request }) => {
    const body = await request.json()
    console.log('예약 요청 데이터:', body)
    return HttpResponse.json({
      message: '예약이 완료되었습니다',
      appointmentId: 9999
    }, { status: 201 })
  }),
]
