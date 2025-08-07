import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // 로그인 관련 상태
    accessToken: localStorage.getItem('access_token') || null,

    // 🔽 로그인한 사용자의 유형
    userType: localStorage.getItem('userType') || null,

    // 변호사 회원가입 데이터 (1~3단계 입력값 저장용)
    signupData: {
      name: '',
      loginEmail: '',
      password: '',
      exam: '',
      registrationNumber: '',
      introduction: '',
      tags: []
    }
  }),

  getters: {
    isLoggedIn: (state) => !!state.accessToken,
    isLawyer: (state) => state.userType === 'LAWYER',
    isAdmin: (state) => state.userType === 'ADMIN',
  },

  actions: {
    // 로그인 관련
    setToken(token) {
      this.accessToken = token
      localStorage.setItem('access_token', token)
    },

    setUserType(type) {
      this.userType = type
      localStorage.setItem('userType', type)
    },

    clearAuth() {
      this.accessToken = null
      this.userType = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('userType')
    },

    // 회원가입 관련
    updateSignup(data) {
      this.signupData = { ...this.signupData, ...data }
    },

    resetSignup() {
      this.signupData = {
        name: '',
        loginEmail: '',
        password: '',
        exam: '',
        registrationNumber: '',
        introduction: '',
        tags: []
      }
    }
  }
})
