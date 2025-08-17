import { http, HttpResponse } from 'msw'
// import { rest } from 'msw'
let appointments = [
  {
    appointmentId: '123',
    clientId: '125',
    lawyerId: '521',
    applicationId: '564',
    appointmentStatus: 'PENDING',
    startTime: null,
    endTime: null,
    createdAt: '2025-07-24 10:02:23'
  },
  {
    appointmentId: '456',
    clientId: '555',
    lawyerId: '521',
    applicationId: '999',
    appointmentStatus: 'APPROVED',
    startTime: '2025-08-01 13:00:00',
    endTime: '2025-08-01 13:30:00',
    createdAt: '2025-07-22 08:30:00'
  }
]

export const handlers = [

  http.get('/api/lawyers/emails/check', ({ request }) => {
    const url = new URL(request.url)
    const email = url.searchParams.get('loginEmail')

    // 이미 등록된 이메일 예시
    const existingEmails = ['lawyer@example.com', 'taein4225@naver.com']

    const isAvailable = !existingEmails.includes(email)

    return HttpResponse.json({
      isAvailable: String(isAvailable) // "true" 또는 "false" 문자열
    })
  }),

  http.post('/api/lawyers/login', async ({ request }) => {
    const body = await request.json()
    const { loginEmail, password } = body

    // 원하는 가짜 조건 추가 가능
    if (loginEmail === 'wjddusdl921@gmail.com' && password === '0123456') {
      return HttpResponse.json({
        accessToken: 'fake-jwt-token-for-test'
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
      tags: ["1", "2", "4"],
    })
  }),

  // ✅ 상담 예약 목록 (오늘 이후를 테스트하기 위해 미래 날짜 포함)
  http.get('/api/appointments/me', ({ request }) => {
    const url = new URL(request.url)
    const status = url.searchParams.get('status')

    let filtered = appointments

    if (status) {
      filtered = appointments.filter(a => a.appointmentStatus === status)
    }

    return HttpResponse.json(filtered)
  }),
   http.patch('/api/appointments/:appointmentId/status', async ({ params, request }) => {
    const { appointmentId } = params
    const body = await request.json()

    const target = appointments.find(a => a.appointmentId === appointmentId)
    if (!target) {
      return HttpResponse.json({ message: 'Appointment not found' }, { status: 404 })
    }

    // 상태 업데이트
    target.appointmentStatus = body.appointmentStatus

    return HttpResponse.json({ message: 'Appointment status updated' })
  }),

  // ✅ 클라이언트 목록
  http.get('/api/admin/clients/list', () => {
    return HttpResponse.json([
      {
        clientId: "125",
        name: '홍길동',
        email: 'client1@example.com'
      },
      {
        clientId: "555",
        name: '이몽룡',
        email: 'client2@example.com'
      }
    ])
  }),

  http.post('/api/ai/pre-consultation', async ({ request }) => {
    const body = await request.json()

    return HttpResponse.json({
      report: {
        issues: ['계약 체결 시 기망 여부', '피해 금액 산정'],
        opinion: '피해 회복 가능성이 높다.',
        sentencePrediction: '징역 8월 ~ 1년 6월',
        confidence: '0.84',
        references: {
          cases: [
            {
              id: '93810',
              name: '소유권이전등기말소',
              court: '대법원',
              year: '1978'
            }
          ],
          statutes: [
            {
              code: '형법',
              article: '347조(사기)'
            }
          ]
        }
      },
      tags: ['형사·사기'],
      recommendedLawyers: [
        {
          lawyerId: '1203',
          loginEmail: 'taein4225@naver.com',
          name: '김태인',
          introduction: '최선을 다하겠습니다!!',
          exam: '로스쿨',
          registrationNumber: '2020-12345',
          certificationStatus: 'APROVED',
          consultationCount: '8',
          tags: ['이혼', '폭행', '음주운전', '상해'],
          matchScore: '0.93',
          photo: '/9j/4AAQSkZJRgABAQEASABIAAD/4QBiRXhpZgAASUkqAAgAAAAHABIBAwABAAAAAQAAABoBBQABAAAAZgAAABsBBQABAAAAagAAACgBAwABAAAAAgAAADEBAgANAAAAcgAAADIBAgAUAAAAegAAAGmHBAABAAAAkAEAAP/bAEMAAwICAwICAwMDAwMEAwMDBAUFBAQFBQUGBggGBgYGBgcICQcJCQoKCwsMDQwMDAwMEA8ODg4NDxAQEBAQEA8ODg7/wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACP/EABcRAQEBAQAAAAAAAAAAAAAAAAEAAwT/2gAIAQEAAD8A9//Z'
        },
        {
          lawyerId: '4506',
          loginEmail: 'lee@example.com',
          name: '이은지',
          introduction: '가정법 분야에서 15년 경력의 전문가입니다.',
          exam: '사법시험',
          registrationNumber: '2010-54321',
          certificationStatus: 'APROVED',
          consultationCount: '15',
          tags: ['이혼', '가정폭력'],
          matchScore: '0.87',
          photo: '/9j/4AAQSkZJRgABAQEASABIAAD/4QBiRXhpZgAASUkqAAgAAAAHABIBAwABAAAAAQAAABoBBQABAAAAZgAAABsBBQABAAAAagAAACgBAwABAAAAAgAAADEBAgANAAAAcgAAADIBAgAUAAAAegAAAGmHBAABAAAAkAEAAP/bAEMAAwICAwICAwMDAwMEAwMDBAUFBAQFBQUGBggGBgYGBgcICQcJCQoKCwsMDQwMDAwMEA8ODg4NDxAQEBAQEA8ODg7/wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACP/EABcRAQEBAQAAAAAAAAAAAAAAAAEAAwT/2gAIAQEAAD8A9//Z'
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
        lawyerId: '1203',
        loginEmail: 'taein4225@naver.com',
        name: '김태인',
        introduction: '최선을 다하겠습니다!!',
        exam: '로스쿨',
        registrationNumber: '2020-12345',
        certificationStatus: 'APROVED',
        consultationCount: '8',
        profile_image: 'https://via.placeholder.com/150',
        tags: [3, 5, 6, 7],
        photo: '/9j/4AAQSkZJRgABAQEASABIAAD/4QBiRXhpZgAASUkqAAgAAAAHABIBAwABAAAAAQAAABoBBQABAAAAZgAAABsBBQABAAAAagAAACgBAwABAAAAAgAAADEBAgANAAAAcgAAADIBAgAUAAAAegAAAGmHBAABAAAAkAEAAP/bAEMAAwICAwICAwMDAwMEAwMDBAUFBAQFBQUGBggGBgYGBgcICQcJCQoKCwsMDQwMDAwMEA8ODg4NDxAQEBAQEA8ODg7/wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACP/EABcRAQEBAQAAAAAAAAAAAAAAAAEAAwT/2gAIAQEAAD8A9//Z'

      },
      {
        lawyerId: '5223',
        loginEmail: 'woo4225@naver.com',
        name: '우영우',
        introduction: '돌고래가 보여요! 천재변호사 우영우입니다.',
        exam: '사법시험',
        registrationNumber: '2022-95126',
        certificationStatus: 'APROVED',
        consultationCount: '100',
        profile_image: 'https://via.placeholder.com/150',
        tags: [1, 2],
        photo: '/9j/4AAQSkZJRgABAQEASABIAAD/4QBiRXhpZgAASUkqAAgAAAAHABIBAwABAAAAAQAAABoBBQABAAAAZgAAABsBBQABAAAAagAAACgBAwABAAAAAgAAADEBAgANAAAAcgAAADIBAgAUAAAAegAAAGmHBAABAAAAkAEAAP/bAEMAAwICAwICAwMDAwMEAwMDBAUFBAQFBQUGBggGBgYGBgcICQcJCQoKCwsMDQwMDAwMEA8ODg4NDxAQEBAQEA8ODg7/wAALCAABAAEBAREA/8QAFAABAAAAAAAAAAAAAAAAAAAACP/EABcRAQEBAQAAAAAAAAAAAAAAAAEAAwT/2gAIAQEAAD8A9//Z'
      }
    ]);
  }),

  // 변호사 전체 리스트 조회 (권한 검사 없는 버전)
  http.get('/api/lawyers/list', () => {
    return HttpResponse.json([
      {
        lawyerId: '1203',
        name: '김태인',
        loginEmail: 'taein4225@naver.com',
        introduction: '최선을 다하겠습니다!!',
        exam: '로스쿨',
        registrationNumber: '2020-12345',
        certificationStatus: 'APROVED',
        consultationCount: '8',
        profile_image: 'https://via.placeholder.com/150',
        tags: [3, 5, 6, 7]
      },
      {
        lawyerId: '5223',
        name: '우영우',
        loginEmail: 'woo4225@naver.com',
        introduction: '돌고래가 보여요! 천재변호사 우영우입니다.',
        exam: '사법시험',
        registrationNumber: '2022-95126',
        certificationStatus: 'APROVED',
        consultationCount: '100',
        profile_image: 'https://via.placeholder.com/150',
        tags: [1, 2]
      }
    ])
  }),
  // 특정 날짜에 변호사 예약 불가 시간 조회
  http.get('/api/lawyers/:lawyerId/unavailable-slot', ({ request, params }) => {
    const url = new URL(request.url)
    const date = url.searchParams.get('date')
    const { lawyerId } = params

    // 변호사별 mock unavailable 시간
    const unavailableMap = {
      '1203': {
        '2025-07-30': ['10:00', '11:30'],
        '2025-07-31': ['09:00', '14:00']
      },
      '9999': {
        '2025-07-30': ['13:00']
      }
    }

    const daySlots = unavailableMap[lawyerId]?.[date] || []

    const result = daySlots.map(time => ({
      lawyerId: lawyerId.toString(),
      startTime: `${date} ${time}:00`,
      endTime: `${date} ${time.slice(0, 2)}:${(parseInt(time.slice(3)) + 30) % 60 === 0 ? '00' : '30'}:00`
    }))

    return HttpResponse.json(result)
  }),


  // 나의 상담신청서 목록
  http.get('/api/applications/me', () => {
    return HttpResponse.json([
      {
        applicationId: 101,
        title: '7월 교통사고 사건 신청서',
        isCompleted: "true"
      },
      {
        applicationId: 102,
        title: '합의 관련 상담 신청서',
        isCompleted: "true"
      }
    ])
  }),

  // 상담 예약 요청
  http.post('/api/appointments', async ({ request }) => {
    const body = await request.json()
    return HttpResponse.json({
      message: '예약이 완료되었습니다',
      appointmentId: 9999
    }, { status: 201 })
  }),

  http.get('/api/clients/me', () => {
    return HttpResponse.json({
      email: 'ssafy123@naver.com',
      oauthname: '김싸피',
      oauthProvider: 'kakao',
      oauthIdentifier: '19249452013'
    })
  }),

]

