import { createRouter, createWebHistory } from 'vue-router'

//회원가입 및 로그인
import SocialLogin from '@/features/auth/user/SocialLogin.vue'
import OAuthCallback from '@/features/auth/user/OAuthCallback.vue'
import SignUpFirst from '@/features/auth/lawyer/SignUpFirst.vue';
import SignUpSecond from '@/features/auth/lawyer/SignUpSecond.vue';
import SignUpThird from '@/features/auth/lawyer/SignUpThird.vue';
import LawyerLogin from '@/features/auth/lawyer/LawyerLogin.vue';
import FindPassword from '@/features/auth/lawyer/FindPassword.vue';
//AI상담

//판례검색
import CaseSearchPage from '@/features/cases/CaseSearchPage.vue'

//화상회의
import PreviewUserView from '@/features/videoconference/PreviewUserView.vue';
import PreviewLawyerView from '@/features/videoconference/PreviewLawyerView.vue';
import CaseDetail from '@/features/cases/CaseDetail.vue';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    //회원가입 및 로그인
    {
      path: '/login',
      component: SocialLogin
    },
    {
      path: '/oauth/callback/:provider',
      component: OAuthCallback
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
    {
      path: '/login/lawyer/find-password',
      name: 'FindPassword',
      component: FindPassword
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

  ],
})

export default router
