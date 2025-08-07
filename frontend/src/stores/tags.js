// src/stores/useTagStore.js
import { TAG_MAP } from '@/constants/lawyerTags'
import { defineStore } from 'pinia'

export const useTagStore = defineStore('tagStore', {
  state: () => ({
    tagMap: TAG_MAP
  }),

  getters: {
    getTagName: (state) => (id) => {
      const tag = state.tagMap.find(t => t.id === Number(id))
      return tag ? tag.name : '알 수 없음'
    }
  }
})
