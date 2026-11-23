<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import logoGrande from '../assets/figma/logo-grande.png'
import ErrosCampo from '../components/ErrosCampo.vue'
import api, { errosDeCampo, mensagemErro } from '../services/api'
import { iniciarSessao, inicioDoPapel } from '../stores/sessao'

const router = useRouter()
const route = useRoute()

const form = reactive({ email: '', senha: '' })
const erros = ref({})
const erroGeral = ref('')
const enviando = ref(false)

function validarNoCliente() {
  const e = {}
  if (!form.email.trim()) e.email = ['Informe o e-mail.']
  if (!form.senha) e.senha = ['Informe a senha.']
  erros.value = e
  return Object.keys(e).length === 0
}

async function entrar() {
  erroGeral.value = ''
  if (!validarNoCliente()) return
  enviando.value = true
  try {
    const { data } = await api.post('/auth/login', form)
    iniciarSessao(data.token, data.usuario)
    router.push(route.query.redirect || inicioDoPapel(data.usuario.papel))
  } catch (erro) {
    erroGeral.value = mensagemErro(erro)
    erros.value = errosDeCampo(erro)
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <section class="secao">
    <div class="container" style="max-width: 400px">
      <img :src="logoGrande" alt="Ti Cuida" style="display: block; width: 99px; height: 147px; margin: 1.2rem auto 2.8rem" />

      <div v-if="route.query.expirada" class="notification is-warning is-light">
        Sua sessão expirou. Entre novamente.
      </div>
      <div v-if="erroGeral" class="notification is-danger is-light" role="alert">{{ erroGeral }}</div>

      <form novalidate @submit.prevent="entrar">
        <div class="field">
          <label class="rotulo-grande" for="email">Usuário</label>
          <input
            id="email"
            v-model="form.email"
            class="input campo-destaque"
            :class="{ 'is-danger': erros.email }"
            type="email"
            autocomplete="email"
            placeholder="Insira seu email"
            required
          />
          <ErrosCampo :mensagens="erros.email" />
        </div>
        <div class="field mt-5">
          <div class="is-flex is-justify-content-space-between is-align-items-flex-end">
            <label class="rotulo-grande" for="senha">Senha</label>
            <span class="texto-pequeno has-text-grey" title="Ainda não disponível">Esqueceu sua senha?</span>
          </div>
          <input
            id="senha"
            v-model="form.senha"
            class="input campo-destaque"
            :class="{ 'is-danger': erros.senha }"
            type="password"
            autocomplete="current-password"
            placeholder="Insira sua senha"
            required
          />
          <ErrosCampo :mensagens="erros.senha" />
        </div>

        <div class="has-text-centered" style="margin-top: 3.4rem">
          <button class="button botao is-grande" :class="{ 'is-loading': enviando }" type="submit" style="min-width: 176px">
            Entrar
          </button>
          <p class="mt-3" style="font-family: var(--fonte-titulo)">
            Não possui uma conta? <RouterLink to="/cadastro">Cadastre-se!</RouterLink>
          </p>
        </div>
      </form>

      <details class="texto-pequeno has-text-grey mt-6">
        <summary>Contas de demonstração</summary>
        <p class="mt-2">Senha de todas: <code>Ticuida@2026</code></p>
        <ul>
          <li>Paciente: <code>paciente@ticuida.dev</code></li>
          <li>Operador: <code>operador.praiadacosta@ticuida.dev</code></li>
        </ul>
      </details>
    </div>
  </section>
</template>
