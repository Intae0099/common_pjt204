import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || null,
  }),
  getters: {
    isLoggedIn: (state) => !!state.accessToken,
  },
  actions: {
    setToken(token) {
      this.accessToken = token
      localStorage.setItem('access_token', token)
    },
    clearToken() {
      this.accessToken = null
      localStorage.removeItem('access_token')
    }
  }
})
