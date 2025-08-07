// src/mocks/browser.js
import { setupWorker } from 'msw/browser' // 이 경로는 올바르게 수정되었습니다.
import { handlers } from './handlers'

// 브라우저에서 사용할 수 있는 worker 생성
export const worker = setupWorker(...handlers)
