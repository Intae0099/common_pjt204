import { createRouter, createWebHistory } from 'vue-router'

//메인페이지
import MainPageView from '@/features/main/MainPageView.vue';

//회원가입 및 로그인
import SocialLogin from '@/features/auth/user/SocialLogin.vue'
import SignUpFirst from '@/features/auth/lawyer/SignUpFirst.vue';
import SignUpSecond from '@/features/auth/lawyer/SignUpSecond.vue';
import SignUpThird from '@/features/auth/lawyer/SignUpThird.vue';
import LawyerLogin from '@/features/auth/lawyer/LawyerLogin.vue';
import KakaoCallback from '@/features/auth/user/KakaoCallback.vue'

// 마이페이지
import LawyerMyPage from '@/features/profile/lawyer/LawyerMyPage.vue';
import UserMyPage from '@/features/profile/user/UserMyPage.vue';
import LawyerProfileUpdate from '@/features/profile/lawyer/LawyerProfileUpdate.vue';
import UserProfileUpdate from '@/features/profile/user/UserProfileUpdate.vue';
import UserConsultHistory from '@/features/profile/user/UserConsultHistory.vue';
import LawyerConsultHistory from '@/features/profile/lawyer/LawyerConsultHistory.vue';

//AI상담
import AiStep from '@/features/ai_consult/AIStep.vue'

//판례검색
import CaseSearchPage from '@/features/cases/CaseSearchPage.vue'
import CaseDetail from '@/features/cases/CaseDetail.vue';


// 상담예약
import LawyerSearch from '@/features/reservation/LawyerSearch.vue'
import DetailReservation from '@/features/reservation/DetailReservation.vue'

// AI 상담 신청서
import ConsultationFormView from '@/features/consultationForm/ConsultationFormView.vue';
//화상회의
import PreviewUserView from '@/features/videoconference/user/PreviewUserView.vue';
import PreviewLawyerView from '@/features/videoconference/lawyer/PreviewLawyerView.vue';
import MeetingRoom from '@/features/videoconference/MeetingRoom.vue';
import ChatbotView from '@/features/chatting/ChatbotView.vue';
import RealtimeChatView from '@/features/chatting/RealtimeChatView.vue';
import RoomManager from '@/features/admin/RoomManager.vue';

//관리자
import LawyerStatusManager from '@/features/admin/LawyerStatusManager.vue';
import AdminClients from '@/features/admin/AdminClients.vue';
import AdminLayout from '@/features/admin/AdminLayout.vue';
import AdminLogin from '@/features/admin/AdminLogin.vue';
import { useAuthStore } from '@/stores/auth';
import LawyerCertifications from '@/features/admin/LawyerCertifications.vue';
import ApplicationListView from '@/features/profile/user/ApplicationListView.vue';



const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Main',
      component: MainPageView
    },
    //회원가입 및 로그인
    {
      path: '/login',
      name : 'SocialLogin',
      component: SocialLogin
    },
    {
    path: '/oauth2/callback/kakao',
    name: 'KakaoCallback',
    component: KakaoCallback
    },
    {
      path: '/signup/step1',
      name: 'SignUpFirst',
      component: SignUpFirst
    },
    {
      path: '/signup/step2',
      name: 'SignUpSecond',
      component: SignUpSecond
    },
    {
      path: '/signup/step3',
      name: 'SignUpThird',
      component: SignUpThird
    },
    {
      path: '/login/lawyer',
      name: 'LawyerLogin',
      component: LawyerLogin
    },

    //AI상담
    {
      path: '/ai-consult',
      name: 'AiConsult',
      component: AiStep
    },


    // 마이페이지
    {
      path: '/lawyer/mypage',
      name: 'LawyerMyPage',
      component: LawyerMyPage
    },
    {
      path: '/user/mypage',
      name: 'UserMyPage',
      component: UserMyPage
    },
    {
      path: '/lawyer/update',
      name: 'LawyerProfileUpdate',
      component: LawyerProfileUpdate
    },
    {
      path: '/lawyer/consult-history',
      name: 'LawyerConsultHistory',
      component: LawyerConsultHistory
    },
    {
      path: '/user/update',
      name: 'UserProfileUpdate',
      component: UserProfileUpdate
    },
    {
      path: '/user/consult-history',
      name: 'UserConsultHistory',
      component: UserConsultHistory
    },
    {
      path: '/user/applications', // ✅ 목록 페이지 라우트 추가
      name: 'ApplicationList',
      component: ApplicationListView
    },

    //판례검색
    {
      path: '/cases/search',
      name:'CasesSearch',
      component: CaseSearchPage,
    },
    // 판례 상세 조회
    {
      path: '/cases/detail/:id',
      name: 'CaseDetail',
      component: CaseDetail,
    },

    // 상담예약
    {
      path: '/lawyers',
      name: 'LawyerSearch',
      component: LawyerSearch
    },
    {
      path: '/lawyers/:id/reservation',
      name: 'DetailReservation',
      component: DetailReservation,
      props: true
    },

    // AI 상담 신청서
    {
      path: '/consult-form',
      name:'ConsultForm',
      component: ConsultationFormView,
    },
    //화상회의
    {
      path: '/videocall/preview/client',
      name: 'PreviewUser',
      component: PreviewUserView,
      meta: { requiresAuth: true },
    },
    {
      path: '/videocall/preview/lawyer',
      name: 'PreviewLawyer',
      component: PreviewLawyerView,
      meta: { requiresAuth: true },
    },
    {
      path: '/meeting',
      name: 'MeetingRoom',
      component: MeetingRoom,
      meta: { requiresAuth: true, hideFooter: true  }
    },
    {
      path: '/chat/chatbot',
      name: 'ChatbotView',
      component: ChatbotView
    },
    {
      path: '/chat/realtimechat',
      name: 'RealtimeChatView',
      component: RealtimeChatView
    },
    {
      path: '/chat/realtimechat',
      name: 'RealtimeChatView',
      component: RealtimeChatView
    },
     {
      path: '/admin',
      component: AdminLayout, // 모든 /admin/* 경로의 부모 레이아웃 역할
      meta: { requiresAdmin: true },
      children: [
        {
          // /admin 경로로 직접 접속 시, 변호사 관리 페이지로 자동 이동시킵니다.
          path: '',
          redirect: { name: 'admin-lawyer-management' }
        },
        {
          // 클라이언트 목록 페이지
          // 경로: /admin/clients
          path: 'clients',
          name: 'admin-clients', // 고유한 이름
          component: AdminClients
        },
        {
          // 변호사 자격 인증 관리 페이지
          // 경로: /admin/lawyers/manage
          path: 'lawyers/manage',
          name: 'admin-lawyer-management', // 고유한 이름
          component: LawyerStatusManager
        },
        {
          // 화상 상담방 강제 종료 페이지
          // 경로: /admin/rooms/manage
          path: 'rooms/manage',
          name: 'admin-room-management', // 고유한 이름
          component: RoomManager
        },
        {
          path: 'lawyers/cert',
          name: 'admin-lawyer-certificate',
          component: LawyerCertifications

        },
        {
          // 화상 상담방 강제 종료 페이지
          // 경로: /admin/rooms/manage
          path: 'login',
          name: 'admin-login', // 고유한 이름
          component: AdminLogin,
          meta: { requiresAdmin: false }
        }
      ]
    },

  ],
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token'); // 일반 사용자 토큰 확인

  // 1. "인증이 필요한 페이지"에 접근하려고 할 때 (meta.requiresAuth === true)
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 1-1. 토큰이 없는 경우 (로그인 안 된 경우)
    if (!token) {
      alert('로그인이 필요합니다.');
      next({ name: 'SocialLogin' }); // 로그인 페이지로 리디렉션
    } else {
      // 1-2. 토큰이 있는 경우, 페이지 접근 허용
      next();
    }
    return; // requiresAuth 관련 로직은 여기서 종료
  }

  const authStore = useAuthStore();
  const isAdminLoggedIn = authStore.isLoggedIn && authStore.userType === 'ADMIN';

  // 1. 접근하려는 경로가 /admin 으로 시작하는지 확인합니다.
  if (to.path.startsWith('/admin')) {

    // 2. 그중에서 /admin/login 페이지인 경우를 따로 처리합니다.
    if (to.name === 'admin-login') {
      // 2-1. 이미 로그인한 관리자가 로그인 페이지에 접근하면
      if (isAdminLoggedIn) {
        // 관리자 메인 페이지로 보냅니다.
        next({ name: 'admin-lawyer-management' });
      } else {
        // 2-2. 로그인이 안 된 사용자라면 정상적으로 로그인 페이지를 보여줍니다.
        next();
      }
    }
    // 3. /admin/login 을 제외한 다른 모든 /admin/* 페이지의 경우
    else {
      // 3-1. 관리자로 로그인 되어 있다면 정상적으로 페이지를 보여줍니다.
      if (isAdminLoggedIn) {
        next();
      } else {
        // 3-2. 로그인 되어있지 않다면 alert를 띄우고 로그인 페이지로 보냅니다.
        alert('관리자 로그인이 필요합니다.');
        next({ name: 'admin-login' });
      }
    }
  }
  // 4. /admin 으로 시작하지 않는 모든 다른 페이지는 자유롭게 접근을 허용합니다.
  else {
    next();
  }
});

router.afterEach(() => {
  window.scrollTo(0, 0);
});

export default router
