<script setup>
import { computed } from 'vue'
import { LOTACAO, tempoRelativo } from '../utils/formatos'

// lotacao: { nivel, atualizado_em } ou null (unidade ainda não informou)
const props = defineProps({ lotacao: { type: Object, default: null } })
const info = computed(() => (props.lotacao ? LOTACAO[props.lotacao.nivel] : null))
</script>

<template>
  <span v-if="info" class="tags has-addons mb-0">
    <span class="tag" :class="info.cor">{{ info.rotulo }}</span>
    <span class="tag is-light">atualizado {{ tempoRelativo(lotacao.atualizado_em) }}</span>
  </span>
  <span v-else class="tag is-light">Lotação não informada</span>
</template>
