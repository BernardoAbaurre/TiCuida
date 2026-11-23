<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import iconeExpandir from '../assets/figma/expandir.svg'
import iconeRecolher from '../assets/figma/recolher.svg'

const route = useRoute()

const PERGUNTAS = [
  {
    id: 'triagem',
    pergunta: 'O que é uma triagem?',
    resposta:
      'É a primeira avaliação de quem procura atendimento, para definir a prioridade. No Ti Cuida você faz uma pré-triagem pelo celular: informa sintomas, intensidade e há quanto tempo começou, e recebe uma prioridade sugerida, calculada por regras simples inspiradas no Protocolo de Manchester. O Ti Cuida não faz diagnóstico: a classificação oficial é feita pela equipe da unidade.',
  },
  {
    id: 'dados',
    pergunta: 'Como altero meus dados?',
    resposta:
      'Entre na sua conta, toque no ícone de usuário no topo da tela e escolha "Meu perfil". Lá você atualiza telefone, contato de emergência e convênio.',
  },
  {
    id: 'lotacao',
    pergunta: 'Como vejo a lotação de clínicas?',
    resposta:
      'Ao terminar a triagem, você vê as unidades que aceitam o seu convênio, com a lotação informada pela própria equipe (baixa, média ou alta) e há quanto tempo foi atualizada. Primeiro aparecem as abertas, depois as menos lotadas e, se você permitir o acesso à localização, as mais próximas.',
  },
  {
    id: 'emergencia',
    pergunta: 'E se for uma emergência?',
    resposta:
      'Se você marcar um sinal de alarme (dor forte no peito, falta de ar intensa, desmaio, convulsão, sangramento intenso, confusão mental ou fraqueza súbita em um lado do corpo), a triagem é interrompida e você é orientado a ligar 192 (SAMU).',
  },
  {
    id: 'termos',
    pergunta: 'Quem vê meus dados?',
    resposta:
      'Somente a equipe da unidade que você escolheu no "Estou indo". Coletamos apenas o necessário para a triagem, seguindo o princípio da minimização de dados da LGPD, e você pode pedir a exclusão a qualquer momento.',
  },
  {
    id: 'cookies',
    pergunta: 'O Ti Cuida usa cookies?',
    resposta:
      'Não usamos cookies de rastreamento nem de publicidade. Guardamos apenas a sua sessão de login no armazenamento local do navegador, que é apagada quando você sai da conta.',
  },
  {
    id: 'contato',
    pergunta: 'Não encontrei minha dúvida',
    resposta:
      'Para dúvidas sobre um atendimento, fale com a recepção da unidade escolhida: o telefone aparece no seu protocolo. Em caso de emergência, ligue 192 (SAMU).',
  },
]

const aberta = ref(null)

// Abre a pergunta indicada no endereço (#termos, #cookies, #contato…), vinda dos links do rodapé
watch(
  () => route.hash,
  (hash) => {
    const id = hash?.slice(1)
    if (PERGUNTAS.some((p) => p.id === id)) aberta.value = id
  },
  { immediate: true },
)

function alternar(id) {
  aberta.value = aberta.value === id ? null : id
}
</script>

<template>
  <section>
    <h1 class="faq-titulo">FAQ</h1>
    <div class="faq" style="max-width: 900px; margin: 0 auto 3rem">
      <div
        v-for="p in PERGUNTAS"
        :id="p.id"
        :key="p.id"
        class="faq-item"
        :class="{ aberto: aberta === p.id }"
      >
        <button
          class="faq-pergunta"
          type="button"
          :aria-expanded="aberta === p.id"
          :aria-controls="`resposta-${p.id}`"
          @click="alternar(p.id)"
        >
          <span>{{ p.pergunta }}</span>
          <img :src="aberta === p.id ? iconeRecolher : iconeExpandir" alt="" />
        </button>
        <div v-if="aberta === p.id" :id="`resposta-${p.id}`" class="faq-resposta">
          <p>{{ p.resposta }}</p>
          <p v-if="p.id === 'emergencia' || p.id === 'contato'" class="mt-3">
            <a href="tel:192">Ligar 192 (SAMU)</a>
          </p>
        </div>
      </div>
    </div>
  </section>
</template>
