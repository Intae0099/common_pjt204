import { createRouter, createWebHistory } from 'vue-router'

//회원가입 및 로그인
import SocialLogin from '@/features/auth/user/SocialLogin.vue'
import OAuthCallback from '@/features/auth/user/OAuthCallback.vue'
import SignUpFirst from '@/features/auth/lawyer/SignUpFirst.vue';
import SignUpSecond from '@/features/auth/lawyer/SignUpSecond.vue';
import SignUpThird from '@/features/auth/lawyer/SignUpThird.vue';

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
    // 루트 → 회원가입 시작 단계로
    {
      path: '/',
      redirect: '/signup/step1'
    },
    {
      path: '/:catchAll(.*)',
      redirect: '/signup/step1'
    },
  ],
})

export default router
