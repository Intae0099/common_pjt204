import { createRouter, createWebHistory } from 'vue-router'

//회원가입 및 로그인
import SocialLogin from '@/features/auth/user/SocialLogin.vue'
import SignUpFirst from '@/features/auth/lawyer/SignUpFirst.vue';
import SignUpSecond from '@/features/auth/lawyer/SignUpSecond.vue';
import SignUpThird from '@/features/auth/lawyer/SignUpThird.vue';
import LawyerLogin from '@/features/auth/lawyer/LawyerLogin.vue';

// 마이페이지
import LawyerMyPage from '@/features/profile/lawyer/LawyerMyPage.vue';
import UserMyPage from '@/features/profile/user/UserMyPage.vue';
import LawyerProfileUpdate from '@/features/profile/lawyer/LawyerProfileUpdate.vue';

//AI상담
import AiStep from '@/features/ai_consult/AIStep.vue'

//판례검색
import CaseSearchPage from '@/features/cases/CaseSearchPage.vue'
import CaseDetail from '@/features/cases/CaseDetail.vue';


// 상담예약
import LawyerSearch from '@/features/reservation/LawyerSearch.vue'
import DetailReservation from '@/features/reservation/DetailReservation.vue'

// AI 상담 신청서


//화상회의
import PreviewUserView from '@/features/videoconference/user/PreviewUserView.vue';
import PreviewLawyerView from '@/features/videoconference/lawyer/PreviewLawyerView.vue';
import MeetingRoom from '@/features/videoconference/MeetingRoom.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    //회원가입 및 로그인
    {
      path: '/login',
      component: SocialLogin
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
      name: 'Lawyermypage',
      component: LawyerMyPage
    },
    {
      path: '/user/mypage',
      name: 'Usermypage',
      component: UserMyPage
    },
    {
      path: '/lawyer/update',
      name: 'LawyerProfileUpdate',
      component: LawyerProfileUpdate
    },
    //판례검색
    {
      path: '/cases/search',
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


    //화상회의
    {
      path: '/videocall/preview/client',
      name: 'PreviewUser',
      component: PreviewUserView,
    },
    {
      path: '/videocall/preview/lawyer',
      name: 'PreviewLawyer',
      component: PreviewLawyerView,
    },
    {
      path: '/meeting',
      name: 'MeetingRoom',
      component: MeetingRoom
    },

  ],
})

export default router
