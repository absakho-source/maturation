import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import apiFetchPlugin from './plugins/apiFetch'

// ✅ Import global du thème DGPPE sobre
import './assets/styles-dgppe-sobre.css'

const app = createApp(App)
app.use(router)
app.use(apiFetchPlugin)
app.mount('#app')
