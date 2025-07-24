// src/mocks/browser.js
import { setupWorker } from 'msw'
import { handlers } from './handlers'

// 브라우저에서 사용할 수 있는 worker 생성
export const worker = setupWorker(...handlers)
