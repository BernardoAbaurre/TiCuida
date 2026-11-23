<script setup>
import { onMounted, ref } from 'vue'
import TagPrioridade from '../components/TagPrioridade.vue'
import api, { mensagemErro } from '../services/api'
import { STATUS, formatarDataHora, formatarTelefone, linkRota } from '../utils/formatos'

const props = defineProps({ id: { type: String, required: true } })

const encaminhamento = ref(null)
const carregando = ref(true)
const erroGeral = ref('')

onMounted(async () => {
  try {
    const lista = (await api.get('/encaminhamentos/meus')).data
    encaminhamento.value = lista.find((e) => String(e.id) === props.id) ?? null
    if (!encaminhamento.value) erroGeral.value = 'Protocolo não encontrado.'
  } catch (erro) {
    erroGeral.value = mensagemErro(erro)
  } finally {
    carregando.value = false
  }
})
</script>

<template>
  <section class="secao">
    <div class="container" style="max-width: 420px">
      <div v-if="erroGeral" class="notification is-danger is-light" role="alert">{{ erroGeral }}</div>
      <progress v-if="carregando" class="progress is-small is-primary" max="100">Carregando</progress>

      <template v-else-if="encaminhamento">
        <div class="popup" style="width: 100%">
          <p class="popup-titulo">TUDO CERTO!</p>
          <p class="popup-texto">
            Sua ida ao <strong>{{ encaminhamento.unidade.nome }}</strong> está confirmada.
          </p>
          <p class="texto-pequeno has-text-grey">Seu protocolo</p>
          <p class="protocolo my-1" aria-label="Protocolo">{{ encaminhamento.protocolo }}</p>
          <p class="mb-4">Apresente este código na recepção.</p>
          <div class="tags is-centered mb-4">
            <TagPrioridade :prioridade="encaminhamento.prioridade" />
            <span class="tag" :class="STATUS[encaminhamento.status].cor">
              {{ STATUS[encaminhamento.status].rotulo }}
            </span>
          </div>
          <a
            class="button botao"
            :href="linkRota(encaminhamento.unidade.latitude, encaminhamento.unidade.longitude)"
            target="_blank"
            rel="noopener"
          >
            Ver rota
          </a>
        </div>

        <div class="cartao mt-5 texto-pequeno">
          <p class="cartao-titulo" style="text-align: left">{{ encaminhamento.unidade.nome }}</p>
          <p>{{ encaminhamento.unidade.endereco }}</p>
          <p v-if="encaminhamento.unidade.telefone" class="mt-1">
            Telefone:
            <a :href="`tel:${encaminhamento.unidade.telefone}`">
              {{ formatarTelefone(encaminhamento.unidade.telefone) }}
            </a>
          </p>
          <p class="has-text-grey mt-1">Enviado em {{ formatarDataHora(encaminhamento.criado_em) }}</p>
          <div class="notification is-warning is-light mt-4 mb-3">
            Se piorar no caminho (dor forte no peito, falta de ar, desmaio), ligue
            <a href="tel:192" class="has-text-weight-bold">192</a>.
          </div>
          <RouterLink to="/meus-atendimentos">Ver meus atendimentos</RouterLink>
        </div>
      </template>
    </div>
  </section>
</template>
