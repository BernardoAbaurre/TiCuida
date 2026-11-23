import { createApp } from 'vue'
import 'bulma/css/bulma.min.css'
import './assets/estilos.css'

import App from './App.vue'
import router from './router'
import { configurarSessaoExpirada } from './services/api'

configurarSessaoExpirada(router)

createApp(App).use(router).mount('#app')
