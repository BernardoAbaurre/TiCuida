// Sessão do usuário (token + dados básicos), guardada no localStorage
// para sobreviver a um recarregamento da página.
import { reactive } from 'vue'

const CHAVE = 'ticuida.sessao'

function carregar() {
  try {
    return JSON.parse(localStorage.getItem(CHAVE)) || {}
  } catch {
    return {}
  }
}

function salvar() {
  try {
    localStorage.setItem(CHAVE, JSON.stringify({ token: sessao.token, usuario: sessao.usuario }))
  } catch {
    /* navegação privada: segue só em memória */
  }
}

export const sessao = reactive({ token: null, usuario: null, ...carregar() })

export function iniciarSessao(token, usuario) {
  sessao.token = token
  sessao.usuario = usuario
  salvar()
}

export function atualizarUsuario(usuario) {
  sessao.usuario = usuario
  salvar()
}

export function encerrarSessao() {
  sessao.token = null
  sessao.usuario = null
  try {
    localStorage.removeItem(CHAVE)
  } catch {
    /* ignora */
  }
}

export function papelAtual() {
  return sessao.usuario?.papel ?? null
}

export function inicioDoPapel(papel = papelAtual()) {
  if (papel === 'operador') return '/unidade'
  if (papel === 'paciente') return '/'
  return '/'
}
