import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import '@/assets/Common.scss'

import { useCasesStore } from '@/stores/cases'

// import.meta.env.DEV (개발 환경인지)와 함께
// VITE_API_MOCKING 변수가 'enabled'인지 추가로 확인합니다.
if (import.meta.env.DEV && import.meta.env.VITE_API_MOCKING === 'enabled') {
  const { worker } = await import('./mocks/browser')
  // worker.start()에 옵션을 추가하는 것을 권장합니다.
  await worker.start({
    onUnhandledRequest: 'bypass', // mock 처리되지 않은 요청은 실제 서버로 전달
  }) // 콘솔에 메시지를 남겨서 활성화 여부를 쉽게 확인
}

const app = createApp(App)

const pinia = createPinia()

app.use(pinia)
app.use(router)

const casesStore = useCasesStore(pinia)
casesStore.initializeSearch()

app.mount('#app')
