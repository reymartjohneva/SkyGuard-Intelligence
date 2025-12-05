import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import Landing from './views/Landing.vue'
import Detection from './views/Detection.vue'

const routes = [
  { path: '/', component: Landing },
  { path: '/detection', component: Detection }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
