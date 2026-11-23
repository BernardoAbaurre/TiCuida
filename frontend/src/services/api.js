// Cliente HTTP da API. Envia o token automaticamente e trata sessão expirada.
import axios from 'axios'
import { encerrarSessao, sessao } from '../stores/sessao'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 15000,
})

api.interceptors.request.use((config) => {
  if (sessao.token) config.headers.Authorization = `Bearer ${sessao.token}`
  return config
})

export function configurarSessaoExpirada(router) {
  api.interceptors.response.use(
    (resposta) => resposta,
    (erro) => {
      const ehLogin = erro.config?.url?.includes('/auth/login')
      if (erro.response?.status === 401 && sessao.token && !ehLogin) {
        encerrarSessao()
        router.push({ path: '/login', query: { expirada: '1' } })
      }
      return Promise.reject(erro)
    },
  )
}

/** Mensagem geral do erro, já em português (vem da API). */
export function mensagemErro(erro) {
  if (erro.response?.data?.erro) return erro.response.data.erro
  if (erro.request) return 'Não foi possível falar com o servidor. Verifique sua conexão.'
  return 'Erro inesperado. Tente novamente.'
}

/** Erros por campo, no formato { campo: ["mensagem"] }. */
export function errosDeCampo(erro) {
  return erro.response?.data?.campos ?? {}
}

export default api
