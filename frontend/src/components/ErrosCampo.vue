<script setup>
defineProps({ mensagens: { type: Array, default: () => [] } })
</script>

<template>
  <p v-for="mensagem in mensagens" :key="mensagem" class="help is-danger">{{ mensagem }}</p>
</template>
