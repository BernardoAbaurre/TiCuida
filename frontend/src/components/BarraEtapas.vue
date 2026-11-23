<script setup>
import setaVoltar from '../assets/figma/seta-voltar.svg'

// Botão circular de voltar + traços indicando a etapa atual (protótipo do Figma)
defineProps({
  total: { type: Number, default: 0 },
  atual: { type: Number, default: 1 },
})
const emit = defineEmits(['voltar'])
</script>

<template>
  <div class="barra-etapas">
    <button class="botao-voltar" type="button" aria-label="Voltar" @click="emit('voltar')">
      <img :src="setaVoltar" alt="" />
    </button>
    <div v-if="total > 1" class="etapas-form" role="img" :aria-label="`Etapa ${atual} de ${total}`">
      <span v-for="n in total" :key="n" :class="{ ativa: n === atual }"></span>
    </div>
  </div>
</template>
