<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import TagLotacao from '../components/TagLotacao.vue'
import TagPrioridade from '../components/TagPrioridade.vue'
import api, { mensagemErro } from '../services/api'
import { sessao } from '../stores/sessao'
import {
  ACOES_STATUS,
  LOTACAO,
  STATUS,
  formatarTelefone,
  rotuloInicio,
  tempoRelativo,
} from '../utils/formatos'

const ATUALIZAR_A_CADA_MS = 30000

const unidadeId = computed(() => sessao.usuario?.unidade?.id)
const unidade = ref(null)
const fila = ref([])
const filtro = ref('ativos')
const aberto = ref(null)
const carregando = ref(true)
const salvandoLotacao = ref('')
const alterando = ref(null)
const erroGeral = ref('')
const ultimaAtualizacao = ref(null)
let temporizador = null

const contagem = computed(() => ({
  a_caminho: fila.value.filter((e) => e.status === 'a_caminho').length,
  chegou: fila.value.filter((e) => e.status === 'chegou').length,
}))

async function carregar() {
  erroGeral.value = ''
  try {
    const [u, f] = await Promise.all([
      api.get(`/unidades/${unidadeId.value}`),
      api.get('/encaminhamentos/fila', { params: { status: filtro.value } }),
    ])
    unidade.value = u.data
    fila.value = f.data.encaminhamentos
    ultimaAtualizacao.value = new Date()
  } catch (erro) {
    erroGeral.value = mensagemErro(erro)
  } finally {
    carregando.value = false
  }
}

async function mudarFiltro(novo) {
  filtro.value = novo
  carregando.value = true
  await carregar()
}

async function registrarLotacao(nivel) {
  salvandoLotacao.value = nivel
  try {
    const { data } = await api.post(`/unidades/${unidadeId.value}/lotacao`, { nivel })
    unidade.value = { ...unidade.value, lotacao: data }
  } catch (erro) {
    erroGeral.value = mensagemErro(erro)
  } finally {
    salvandoLotacao.value = ''
  }
}

async function mudarStatus(encaminhamento, status) {
  alterando.value = `${encaminhamento.id}-${status}`
  try {
    await api.patch(`/encaminhamentos/${encaminhamento.id}`, { status })
    await carregar()
  } catch (erro) {
    erroGeral.value = mensagemErro(erro)
  } finally {
    alterando.value = null
  }
}

onMounted(() => {
  carregar()
  temporizador = setInterval(carregar, ATUALIZAR_A_CADA_MS)
})
onUnmounted(() => clearInterval(temporizador))
</script>

<template>
  <section class="secao">
    <div class="container">
      <div class="is-flex is-justify-content-space-between is-align-items-center is-flex-wrap-wrap mb-4">
        <div>
          <h1 class="titulo-pagina mb-1" style="font-size: 1.6rem">{{ sessao.usuario?.unidade?.nome }}</h1>
          <p class="texto-pequeno has-text-grey">
            Fila de pré-triagens · atualiza a cada 30 s
            <template v-if="ultimaAtualizacao">
              (última: {{ ultimaAtualizacao.toLocaleTimeString('pt-BR') }})
            </template>
          </p>
        </div>
        <button class="button botao is-pequeno is-escuro" type="button" @click="carregar">Atualizar agora</button>
      </div>

      <div v-if="erroGeral" class="notification is-danger is-light" role="alert">{{ erroGeral }}</div>

      <div class="columns">
        <!-- Lotação -->
        <div class="column is-4">
          <div class="cartao mb-4">
            <h2 class="cartao-titulo" style="text-align: left">Lotação da unidade</h2>
            <div class="mb-3">
              <TagLotacao v-if="unidade" :lotacao="unidade.lotacao" />
            </div>
            <p class="texto-pequeno has-text-grey mb-2">Informe a situação atual:</p>
            <div class="buttons">
              <button
                v-for="(info, nivel) in LOTACAO"
                :key="nivel"
                class="button"
                :class="[info.cor, { 'is-light': unidade?.lotacao?.nivel !== nivel, 'is-loading': salvandoLotacao === nivel }]"
                type="button"
                @click="registrarLotacao(nivel)"
              >
                {{ info.curto }}
              </button>
            </div>
          </div>
          <div class="cartao mb-4">
            <p class="texto-pequeno">A caminho: <strong>{{ contagem.a_caminho }}</strong></p>
            <p class="texto-pequeno">Na unidade (chegou): <strong>{{ contagem.chegou }}</strong></p>
          </div>
        </div>

        <!-- Fila -->
        <div class="column">
          <div class="tabs is-toggle is-small mb-4">
            <ul>
              <li :class="{ 'is-active': filtro === 'ativos' }">
                <a href="#" @click.prevent="mudarFiltro('ativos')">Em andamento</a>
              </li>
              <li :class="{ 'is-active': filtro === 'todos' }">
                <a href="#" @click.prevent="mudarFiltro('todos')">Todos</a>
              </li>
            </ul>
          </div>

          <progress v-if="carregando" class="progress is-small is-primary" max="100">Carregando</progress>
          <div v-else-if="!fila.length" class="notification is-light">Nenhuma pré-triagem na fila.</div>

          <div v-for="e in fila" :key="e.id" class="cartao mb-4" :class="`borda-prioridade-${e.prioridade}`">
            <div class="is-flex is-justify-content-space-between is-flex-wrap-wrap">
              <div class="mb-2">
                <p class="has-text-weight-semibold" style="color: var(--azul)">{{ e.paciente.nome }}, {{ e.paciente.idade }} anos</p>
                <p class="texto-pequeno has-text-grey">
                  Protocolo <strong>{{ e.protocolo }}</strong> · enviado {{ tempoRelativo(e.criado_em) }}
                </p>
              </div>
              <div class="tags">
                <TagPrioridade :prioridade="e.prioridade" />
                <span class="tag" :class="STATUS[e.status].cor">{{ STATUS[e.status].rotulo }}</span>
              </div>
            </div>
            <p class="mb-2">{{ e.triagem.queixa_principal }}</p>

            <div v-if="aberto === e.id" class="content texto-pequeno mb-3">
              <table class="table is-narrow is-fullwidth">
                <tbody>
                  <tr>
                    <th>Sintomas</th>
                    <td>{{ e.triagem.sintomas.map((s) => s.nome).join(', ') || 'Nenhum marcado' }}</td>
                  </tr>
                  <tr><th>Intensidade</th><td>{{ e.triagem.intensidade }} de 10</td></tr>
                  <tr><th>Início</th><td>{{ rotuloInicio(e.triagem.inicio_sintomas) }}</td></tr>
                  <tr>
                    <th>Temperatura</th>
                    <td>{{ e.triagem.temperatura != null ? `${e.triagem.temperatura} °C` : 'Não medida' }}</td>
                  </tr>
                  <tr><th>CPF</th><td>{{ e.paciente.cpf }}</td></tr>
                  <tr><th>Celular</th><td>{{ formatarTelefone(e.paciente.telefone) }}</td></tr>
                  <tr>
                    <th>Contato de emergência</th>
                    <td>{{ e.paciente.contato_emergencia_nome }} – {{ formatarTelefone(e.paciente.contato_emergencia_telefone) }}</td>
                  </tr>
                  <tr>
                    <th>Convênio</th>
                    <td>{{ e.paciente.convenio }}<template v-if="e.paciente.numero_carteirinha"> ({{ e.paciente.numero_carteirinha }})</template></td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div class="buttons">
              <button class="button is-small is-light" type="button" @click="aberto = aberto === e.id ? null : e.id">
                {{ aberto === e.id ? 'Ocultar detalhes' : 'Ver detalhes' }}
              </button>
              <button
                v-for="status in e.transicoes_permitidas"
                :key="status"
                class="button is-small"
                :class="[ACOES_STATUS[status].cor, { 'is-loading': alterando === `${e.id}-${status}` }]"
                type="button"
                @click="mudarStatus(e, status)"
              >
                {{ ACOES_STATUS[status].rotulo }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>
