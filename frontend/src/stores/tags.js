// src/stores/useTagStore.js
import { defineStore } from 'pinia'

export const useTagStore = defineStore('tagStore', {
  state: () => ({
    tagMap: [
      { id: 1, name: '형사 분야' },
      { id: 2, name: '교통·사고·보험' },
      { id: 3, name: '가사·가족' },
      { id: 4, name: '민사·계약·채권' },
      { id: 5, name: '파산·회생·채무조정' },
      { id: 6, name: '상속·증여' },
      { id: 7, name: '지식재산권' },
      { id: 8, name: '노동·고용' },
      { id: 9, name: '행정·조세' },
      { id: 10, name: '환경·공공' },
      { id: 11, name: '의료·생명·개인정보' },
      { id: 12, name: '금융·증권·기업' }
    ]
  }),

  getters: {
    getTagName: (state) => (id) => {
      const tag = state.tagMap.find(t => t.id === Number(id))
      return tag ? tag.name : '알 수 없음'
    }
  }
})
