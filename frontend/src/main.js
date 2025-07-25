import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import '@/assets/Common.scss'

if (import.meta.env.DEV) {
  const { worker } = await import('./mocks/browser')
  await worker.start()
}

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
