import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // 로그인 관련 상태
    accessToken: localStorage.getItem('access_token') || null,

    // 변호사 회원가입 데이터 (1~3단계 입력값 저장용)
    signupData: {
      name: '',
      email: '',
      password: '',
      phone: '',
      officeNumber: '',
      exam: '',
      examRound: '',
      careerYears: '',
      introduction: '',
      tags: []
    }
  }),

  getters: {
    isLoggedIn: (state) => !!state.accessToken,
  },

  actions: {
    // 로그인 관련
    setToken(token) {
      this.accessToken = token
      localStorage.setItem('access_token', token)
    },
    clearToken() {
      this.accessToken = null
      localStorage.removeItem('access_token')
    },

    // 회원가입 관련
    updateSignup(data) {
      this.signupData = { ...this.signupData, ...data }
    },
    resetSignup() {
      this.signupData = {
        name: '',
        email: '',
        password: '',
        phone: '',
        officeNumber: '',
        exam: '',
        examRound: '',
        careerYears: '',
        introduction: '',
        tags: []
      }
    }
  }
})
