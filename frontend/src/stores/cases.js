// src/stores/cases.js

import { defineStore } from 'pinia';
import axios from 'axios';

const API_URL = 'http://122.38.210.80:8997/api';

export const useCasesStore = defineStore('cases', {
  /**
   * State: 상태 정의
   */
  state: () => ({
    query: '',
    sortOption: 'accuracy',
    // --- 페이지네이션을 위한 상태 추가 ---
    _allCaseList: [], // API로부터 받은 전체 목록 (20개)을 저장할 내부 상태
    currentPage: 1,   // 클라이언트 측 현재 페이지 번호
    itemsPerPage: 5,  // 한 페이지에 보여줄 아이템 개수
    // -------------------------------------
    pagination: null, // API의 페이징 정보 (hasNext 등)
    isLoading: false,
    error: null,
    searchPerformed: false,
  }),

  /**
   * Getters: 계산된 상태
   */
  getters: {
    // API 결과가 있는지 여부 (전체 목록 기준)
    hasResults: (state) => state._allCaseList.length > 0,

    // ✨ [핵심] 현재 페이지에 보여줄 5개의 아이템만 잘라서 반환하는 getter
    paginatedCaseList: (state) => {
      const start = (state.currentPage - 1) * state.itemsPerPage;
      const end = start + state.itemsPerPage;
      return state._allCaseList.slice(start, end);
    },

    // 전체 페이지 수를 계산하는 getter
    totalPages: (state) => {
      return Math.ceil(state._allCaseList.length / state.itemsPerPage);
    }
  },

  /**
   * Actions: 상태 변경 로직
   */
  actions: {
    async initializeSearch() {
      // 아직 검색이 수행되지 않았고, 결과 목록도 비어있을 때만 실행
      if (!this.searchPerformed && this._allCaseList.length === 0) {
        this.query = '교통사고'; // 기본 검색어 설정
        await this.searchCases();   // 기존 검색 액션 호출
        this.query = '';
      }
    },
    async searchCases() {
      // ... (기존 검색어 체크 로직은 동일)
      if (this.query.length < 2) {
        this.error = '검색어는 2자 이상 입력해주세요.';
        this._allCaseList = [];
        this.searchPerformed = true;
        return;
      }

      this.isLoading = true;
      this.error = null;
      this.searchPerformed = true;

      try {
        const response = await axios.get(`${API_URL}/search/cases`, {
          params: {
            keyword: this.query,
            page: 1,
            size: 20, // ✨ API 요청 시 20개 데이터를 받아옵니다.
          },
        });

        if (response.data.success && Array.isArray(response.data.data)) {
          const items = response.data.data;

          const pageMeta = {
            total: response.data.total,
            page: response.data.page,
            size: response.data.size,
            pages: response.data.pages,
          };

          const processedItems = items.map(item => {
            if (item.summary && item.summary.length > 300) {
              return { ...item, summary: item.summary.substring(0, 300) + '...' };
            }
            return item;
          });

          // 가공된 전체 데이터를 `_allCaseList`에 저장합니다.
          this._allCaseList = processedItems;
          this.pagination = pageMeta; // API의 페이지 정보 저장
          this.currentPage = 1; // ✨ 새로운 검색 시 항상 1페이지로 리셋

        } else {
          this._allCaseList = [];
          this.pagination = null;
          throw new Error(response.data.message || '데이터를 가져오는데 실패했습니다.');
        }

      } catch (err) {
        this.error = err.message || '검색 중 오류가 발생했습니다.';
        this._allCaseList = [];
        this.pagination = null;
      } finally {
        this.isLoading = false;
      }
    },

    // ✨ 페이지 번호를 변경하는 액션
    setPage(pageNumber) {
      if (pageNumber > 0 && pageNumber <= this.totalPages) {
        this.currentPage = pageNumber;
      }
    },

    resetSearchState() {
      this.query = '';
      this.sortOption = 'accuracy';
      this._allCaseList = [];
      this.pagination = null;
      this.isLoading = false;
      this.error = null;
      this.searchPerformed = false;
      this.currentPage = 1;
    }
  },
});
