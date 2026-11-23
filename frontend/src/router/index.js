import { createRouter, createWebHistory } from 'vue-router'
import { inicioDoPapel, papelAtual, sessao } from '../stores/sessao'

// meta.papel: rota só para esse papel; meta.visitante: só para quem NÃO está logado
const routes = [
  { path: '/', component: () => import('../views/InicioView.vue') },
  { path: '/sobre', component: () => import('../views/SobreView.vue') },
  { path: '/login', component: () => import('../views/LoginView.vue'), meta: { visitante: true } },
  {
    path: '/cadastro',
    component: () => import('../views/CadastroView.vue'),
    meta: { visitante: true },
  },
  {
    path: '/triagem',
    component: () => import('../views/TriagemView.vue'),
    meta: { papel: 'paciente' },
  },
  {
    path: '/triagem/:id',
    component: () => import('../views/ResultadoView.vue'),
    meta: { papel: 'paciente' },
    props: true,
  },
  {
    path: '/protocolo/:id',
    component: () => import('../views/ProtocoloView.vue'),
    meta: { papel: 'paciente' },
    props: true,
  },
  {
    path: '/meus-atendimentos',
    component: () => import('../views/HistoricoView.vue'),
    meta: { papel: 'paciente' },
  },
  {
    path: '/perfil',
    component: () => import('../views/PerfilView.vue'),
    meta: { papel: 'paciente' },
  },
  {
    path: '/unidade',
    component: () => import('../views/FilaView.vue'),
    meta: { papel: 'operador' },
  },
  { path: '/:caminho(.*)*', component: () => import('../views/NaoEncontradoView.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: (destino) => (destino.hash ? { el: destino.hash, top: 16 } : { top: 0 }),
})

router.beforeEach((destino) => {
  const logado = Boolean(sessao.token)
  if (destino.meta.visitante && logado) return inicioDoPapel()
  if (destino.meta.papel) {
    if (!logado) return { path: '/login', query: { redirect: destino.fullPath } }
    if (papelAtual() !== destino.meta.papel) return inicioDoPapel()
  }
  if (destino.path === '/' && papelAtual() === 'operador') return '/unidade'
  return true
})

export default router
