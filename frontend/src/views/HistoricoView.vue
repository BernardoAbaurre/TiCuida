<script setup>
import { computed, onMounted, ref } from 'vue'
import TagPrioridade from '../components/TagPrioridade.vue'
import api, { mensagemErro } from '../services/api'
import { STATUS, formatarDataHora } from '../utils/formatos'

const triagens = ref([])
const encaminhamentos = ref([])
const carregando = ref(true)
const erroGeral = ref('')

const porTriagem = computed(() => Object.fromEntries(encaminhamentos.value.map((e) => [e.triagem_id, e])))

onMounted(async () => {
  try {
    const [t, e] = await Promise.all([api.get('/triagens'), api.get('/encaminhamentos/meus')])
    triagens.value = t.data
    encaminhamentos.value = e.data
  } catch (erro) {
    erroGeral.value = mensagemErro(erro)
  } finally {
    carregando.value = false
  }
})
</script>

<template>
  <section class="secao">
    <div class="container" style="max-width: 720px">
      <div class="is-flex is-justify-content-space-between is-align-items-center is-flex-wrap-wrap mb-4" style="gap: 1rem">
        <h1 class="titulo-pagina mb-0">Meus atendimentos</h1>
        <RouterLink to="/triagem" class="button botao is-pequeno">Nova triagem</RouterLink>
      </div>

      <div v-if="erroGeral" class="notification is-danger is-light" role="alert">{{ erroGeral }}</div>
      <progress v-if="carregando" class="progress is-small is-primary" max="100">Carregando</progress>

      <div v-else-if="!triagens.length" class="cartao has-text-centered">
        <p class="mb-4">Você ainda não fez nenhuma triagem.</p>
        <RouterLink to="/triagem" class="button botao">Iniciar triagem</RouterLink>
      </div>

      <div v-for="t in triagens" :key="t.id" class="cartao mb-4" :class="`borda-prioridade-${t.prioridade}`">
        <div class="is-flex is-justify-content-space-between is-flex-wrap-wrap mb-2">
          <span class="texto-pequeno has-text-grey">{{ formatarDataHora(t.criada_em) }}</span>
          <TagPrioridade :prioridade="t.prioridade" />
        </div>
        <p class="mb-2" style="font-weight: 500">{{ t.queixa_principal }}</p>

        <template v-if="porTriagem[t.id]">
          <p class="texto-pequeno">
            {{ porTriagem[t.id].unidade.nome }} · protocolo
            <strong>{{ porTriagem[t.id].protocolo }}</strong>
            <span class="tag ml-2" :class="STATUS[porTriagem[t.id].status].cor">
              {{ STATUS[porTriagem[t.id].status].rotulo }}
            </span>
          </p>
          <RouterLink :to="`/protocolo/${porTriagem[t.id].id}`" class="texto-pequeno">Ver protocolo</RouterLink>
        </template>
        <RouterLink v-else-if="t.prioridade !== 'emergencia'" :to="`/triagem/${t.id}`" class="texto-pequeno">
          Escolher unidade
        </RouterLink>
        <p v-else class="texto-pequeno has-text-danger">Orientado a ligar para o 192.</p>
      </div>
    </div>
  </section>
</template>
