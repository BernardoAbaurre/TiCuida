<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import BarraEtapas from '../components/BarraEtapas.vue'
import ErrosCampo from '../components/ErrosCampo.vue'
import api, { errosDeCampo, mensagemErro } from '../services/api'
import { iniciarSessao } from '../stores/sessao'
import { mascararCpf, somenteDigitos } from '../utils/formatos'

const router = useRouter()

const convenios = ref([])
const form = reactive({
  nome: '',
  cpf: '',
  data_nascimento: '',
  telefone: '',
  email: '',
  senha: '',
  contato_emergencia_nome: '',
  contato_emergencia_telefone: '',
  convenio_id: '',
  numero_carteirinha: '',
  consentimento: false,
})
const confirmarSenha = ref('')
const erros = ref({})
const erroGeral = ref('')
const enviando = ref(false)

onMounted(async () => {
  try {
    convenios.value = (await api.get('/convenios')).data
  } catch (erro) {
    erroGeral.value = mensagemErro(erro)
  }
})

// Validação no navegador para dar retorno rápido. A API valida tudo de novo.
function validarNoCliente() {
  const e = {}
  const obrigatorio = 'Campo obrigatório.'
  if (form.nome.trim().length < 3) e.nome = ['Informe o nome completo.']
  if (somenteDigitos(form.cpf).length !== 11) e.cpf = ['O CPF deve ter 11 dígitos.']
  if (!form.data_nascimento) e.data_nascimento = [obrigatorio]
  if (![10, 11].includes(somenteDigitos(form.telefone).length)) e.telefone = ['Informe DDD + número.']
  if (!/^\S+@\S+\.\S+$/.test(form.email)) e.email = ['E-mail inválido.']
  if (form.senha.length < 8 || !/\d/.test(form.senha) || !/[A-Za-z]/.test(form.senha))
    e.senha = ['Mínimo de 8 caracteres, com letras e números.']
  if (confirmarSenha.value !== form.senha) e.confirmar_senha = ['As senhas não conferem.']
  if (form.contato_emergencia_nome.trim().length < 3) e.contato_emergencia_nome = [obrigatorio]
  if (![10, 11].includes(somenteDigitos(form.contato_emergencia_telefone).length))
    e.contato_emergencia_telefone = ['Informe DDD + número.']
  if (!form.convenio_id) e.convenio_id = ['Escolha o convênio (ou Particular).']
  if (!form.consentimento) e.consentimento = ['É preciso aceitar o termo para continuar.']
  erros.value = e
  return Object.keys(e).length === 0
}

async function cadastrar() {
  erroGeral.value = ''
  if (!validarNoCliente()) {
    erroGeral.value = 'Corrija os campos destacados.'
    return
  }
  enviando.value = true
  try {
    const { data } = await api.post('/auth/cadastro', { ...form, convenio_id: Number(form.convenio_id) })
    iniciarSessao(data.token, data.usuario)
    router.push('/triagem')
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
      <BarraEtapas @voltar="router.back()" />
      <h1 class="titulo-pagina">Cadastro</h1>

      <div v-if="erroGeral" class="notification is-danger is-light" role="alert">{{ erroGeral }}</div>

      <form novalidate @submit.prevent="cadastrar">
        <div class="field">
          <label class="rotulo" for="nome">Nome <span class="obrigatorio">*</span></label>
          <input
            id="nome"
            v-model="form.nome"
            class="input campo"
            :class="{ 'is-danger': erros.nome }"
            autocomplete="name"
            placeholder="Nome completo"
          />
          <ErrosCampo :mensagens="erros.nome" />
        </div>

        <div class="field">
          <label class="rotulo" for="nascimento">Data de nascimento <span class="obrigatorio">*</span></label>
          <input
            id="nascimento"
            v-model="form.data_nascimento"
            class="input campo campo-curto"
            :class="{ 'is-danger': erros.data_nascimento }"
            type="date"
            autocomplete="bday"
          />
          <ErrosCampo :mensagens="erros.data_nascimento" />
        </div>

        <div class="columns is-mobile is-variable is-3 mb-0">
          <div class="column">
            <div class="field">
              <label class="rotulo" for="telefone">Telefone <span class="obrigatorio">*</span></label>
              <input
                id="telefone"
                v-model="form.telefone"
                class="input campo"
                :class="{ 'is-danger': erros.telefone }"
                type="tel"
                autocomplete="tel"
                placeholder="(XX) XXXXX-XXXX"
              />
              <ErrosCampo :mensagens="erros.telefone" />
            </div>
          </div>
          <div class="column">
            <div class="field">
              <label class="rotulo" for="cpf">CPF <span class="obrigatorio">*</span></label>
              <input
                id="cpf"
                :value="form.cpf"
                class="input campo"
                :class="{ 'is-danger': erros.cpf }"
                inputmode="numeric"
                placeholder="Insira seu CPF"
                @input="form.cpf = mascararCpf($event.target.value); $event.target.value = form.cpf"
              />
              <ErrosCampo :mensagens="erros.cpf" />
            </div>
          </div>
        </div>

        <div class="field">
          <label class="rotulo" for="email">E-mail <span class="obrigatorio">*</span></label>
          <input
            id="email"
            v-model="form.email"
            class="input campo"
            :class="{ 'is-danger': erros.email }"
            type="email"
            autocomplete="email"
            placeholder="Insira seu e-mail"
          />
          <ErrosCampo :mensagens="erros.email" />
        </div>

        <div class="field">
          <label class="rotulo" for="senha">Senha <span class="obrigatorio">*</span></label>
          <input
            id="senha"
            v-model="form.senha"
            class="input campo"
            :class="{ 'is-danger': erros.senha }"
            type="password"
            autocomplete="new-password"
            placeholder="Mínimo de 8 caracteres, com letras e números"
          />
          <ErrosCampo :mensagens="erros.senha" />
        </div>

        <div class="field">
          <label class="rotulo" for="confirmar-senha">Confirmar senha <span class="obrigatorio">*</span></label>
          <input
            id="confirmar-senha"
            v-model="confirmarSenha"
            class="input campo"
            :class="{ 'is-danger': erros.confirmar_senha }"
            type="password"
            autocomplete="new-password"
            placeholder="Confirme sua senha"
          />
          <ErrosCampo :mensagens="erros.confirmar_senha" />
        </div>

        <p class="rotulo mt-4">Contato de emergência <span class="obrigatorio">*</span></p>
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
          <label class="rotulo" for="convenio">Empresa <span class="obrigatorio">*</span></label>
          <div class="select campo" :class="{ 'is-danger': erros.convenio_id }">
            <select id="convenio" v-model="form.convenio_id">
              <option value="" disabled>Escolha… (ou Particular)</option>
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

        <div class="cartao mt-6 mb-4 texto-pequeno">
          <p class="mb-3">
            <strong>Termo de consentimento (LGPD).</strong> Seus dados de saúde são sensíveis. Eles serão usados
            apenas para sugerir a prioridade do atendimento e serão enviados somente para a unidade que você
            escolher. Você pode pedir a exclusão a qualquer momento.
          </p>
          <label class="item-check" style="justify-content: flex-start">
            <input v-model="form.consentimento" type="checkbox" />
            <span>Li e concordo com o uso dos meus dados para a pré-triagem.</span>
          </label>
          <ErrosCampo :mensagens="erros.consentimento" />
        </div>

        <div class="acoes-form is-align-items-center is-justify-content-space-between">
          <span class="texto-pequeno">Já tem conta? <RouterLink to="/login">Entrar</RouterLink></span>
          <button class="button botao" :class="{ 'is-loading': enviando }" type="submit">Cadastrar</button>
        </div>
      </form>
    </div>
  </section>
</template>
