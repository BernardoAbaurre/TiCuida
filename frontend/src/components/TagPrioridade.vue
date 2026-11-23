<script setup>
import { computed } from 'vue'
import { PRIORIDADES } from '../utils/formatos'

const props = defineProps({
  prioridade: { type: String, required: true },
  grande: { type: Boolean, default: false },
})
const info = computed(() => PRIORIDADES[props.prioridade] ?? { rotulo: props.prioridade, cor: '' })
</script>

<template>
  <span class="tag" :class="[info.cor, { 'is-medium': grande }]">{{ info.rotulo }}</span>
</template>
