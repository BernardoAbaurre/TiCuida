<script setup>
import { onMounted, reactive, ref } from 'vue'
import iconeUsuario from '../assets/figma/icone-usuario.png'
import ErrosCampo from '../components/ErrosCampo.vue'
import api, { errosDeCampo, mensagemErro } from '../services/api'
import { atualizarUsuario, sessao } from '../stores/sessao'
import { formatarData, mascararCpf, somenteDigitos } from '../utils/formatos'

const perfil = ref(null)
const convenios = ref([])
const form = reactive({
  telefone: '',
  contato_emergencia_nome: '',
  contato_emergencia_telefone: '',
  convenio_id: '',
  numero_carteirinha: '',
})
const erros = ref({})
const erroGeral = ref('')
const sucesso = ref(false)
const carregando = ref(true)
const enviando = ref(false)

function preencher(dados) {
  perfil.value = dados
  form.telefone = dados.telefone
  form.contato_emergencia_nome = dados.contato_emergencia_nome
  form.contato_emergencia_telefone = dados.contato_emergencia_telefone
  form.convenio_id = dados.convenio?.id ?? ''
  form.numero_carteirinha = dados.numero_carteirinha ?? ''
}

onMounted(async () => {
  try {
    const [p, c] = await Promise.all([api.get('/pacientes/me'), api.get('/convenios')])
    preencher(p.data)
    convenios.value = c.data
  } catch (erro) {
    erroGeral.value = mensagemErro(erro)
  } finally {
    carregando.value = false
  }
})

function validarNoCliente() {
  const e = {}
  if (![10, 11].includes(somenteDigitos(form.telefone).length)) e.telefone = ['Informe DDD + número.']
  if (form.contato_emergencia_nome.trim().length < 3) e.contato_emergencia_nome = ['Campo obrigatório.']
  if (![10, 11].includes(somenteDigitos(form.contato_emergencia_telefone).length))
    e.contato_emergencia_telefone = ['Informe DDD + número.']
  erros.value = e
  return Object.keys(e).length === 0
}

async function salvar() {
  sucesso.value = false
  erroGeral.value = ''
  if (!validarNoCliente()) return
  enviando.value = true
  try {
    const { data } = await api.put('/pacientes/me', { ...form, convenio_id: Number(form.convenio_id) })
    preencher(data)
    atualizarUsuario({ ...sessao.usuario, paciente: data })
    sucesso.value = true
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
    <div class="container" style="max-width: 720px">
      <div class="perfil-topo">
        <span class="perfil-avatar"><img :src="iconeUsuario" alt="" /></span>
        <h1 class="titulo-pagina">Perfil</h1>
      </div>

      <div v-if="erroGeral" class="notification is-danger is-light" role="alert">{{ erroGeral }}</div>
      <div v-if="sucesso" class="notification is-success is-light" role="status">Dados atualizados.</div>
      <progress v-if="carregando" class="progress is-small is-primary" max="100">Carregando</progress>

      <form v-else-if="perfil" novalidate @submit.prevent="salvar">
        <div class="field">
          <label class="rotulo" for="nome">Nome</label>
          <input id="nome" class="input campo" :value="perfil.nome" readonly />
        </div>
        <div class="field">
          <label class="rotulo" for="nascimento">Data de nascimento</label>
          <input
            id="nascimento"
            class="input campo campo-curto"
            :value="`${formatarData(perfil.data_nascimento)} (${perfil.idade} anos)`"
            readonly
          />
        </div>
        <div class="columns is-mobile is-variable is-3 mb-0">
          <div class="column">
            <div class="field">
              <label class="rotulo" for="telefone">Telefone</label>
              <input
                id="telefone"
                v-model="form.telefone"
                class="input campo"
                :class="{ 'is-danger': erros.telefone }"
                type="tel"
                placeholder="(XX) XXXXX-XXXX"
              />
              <ErrosCampo :mensagens="erros.telefone" />
            </div>
          </div>
          <div class="column">
            <div class="field">
              <label class="rotulo" for="cpf">CPF</label>
              <input id="cpf" class="input campo" :value="mascararCpf(perfil.cpf)" readonly />
            </div>
          </div>
        </div>
        <div class="field">
          <label class="rotulo" for="email">E-mail</label>
          <input id="email" class="input campo" :value="sessao.usuario?.email" readonly />
        </div>

        <p class="rotulo mt-4">Contato de emergência</p>
        <div class="columns is-mobile is-variable is-3 mb-0">
          <div class="column">
            <div class="field">
              <label class="is-sr-only" for="contato-nome">Nome do contato de emergência</label>
              <input
                id="contato-nome"
                v-model="form.contato_emergencia_nome"
                class="input campo"
                :class="{ 'is-danger': erros.contato_emergencia_nome }"
                placeholder="Nome"
              />
              <ErrosCampo :mensagens="erros.contato_emergencia_nome" />
            </div>
          </div>
          <div class="column">
            <div class="field">
              <label class="is-sr-only" for="contato-tel">Telefone do contato de emergência</label>
              <input
                id="contato-tel"
                v-model="form.contato_emergencia_telefone"
                class="input campo"
                :class="{ 'is-danger': erros.contato_emergencia_telefone }"
                type="tel"
                placeholder="(XX) XXXXX-XXXX"
              />
              <ErrosCampo :mensagens="erros.contato_emergencia_telefone" />
            </div>
          </div>
        </div>

        <h2 class="titulo-secao">Convênio</h2>
        <div class="field">
          <label class="rotulo" for="convenio">Empresa</label>
          <div class="select campo">
            <select id="convenio" v-model="form.convenio_id">
              <option v-for="c in convenios" :key="c.id" :value="c.id">{{ c.nome }}</option>
            </select>
          </div>
          <ErrosCampo :mensagens="erros.convenio_id" />
        </div>
        <div class="field">
          <label class="rotulo" for="carteirinha">Código</label>
          <input
            id="carteirinha"
            v-model="form.numero_carteirinha"
            class="input campo campo-curto"
            placeholder="Código do convênio"
          />
          <ErrosCampo :mensagens="erros.numero_carteirinha" />
        </div>

        <div class="acoes-form">
          <button class="button botao" :class="{ 'is-loading': enviando }" type="submit">Salvar</button>
        </div>
      </form>
    </div>
  </section>
</template>
