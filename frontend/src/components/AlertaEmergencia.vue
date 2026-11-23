<script setup>
defineProps({ orientacao: { type: String, default: '' } })
</script>

<template>
  <article class="message is-danger" role="alert">
    <div class="message-header">
      <p>Emergência: procure ajuda agora</p>
    </div>
    <div class="message-body">
      <p class="mb-4">
        {{ orientacao || 'Sinal de alarme identificado. Ligue agora para o SAMU (192) ou vá à emergência mais próxima.' }}
      </p>
      <a href="tel:192" class="button is-danger is-large is-fullwidth has-text-weight-bold">
        Ligar para o SAMU – 192
      </a>
      <p class="mt-4 texto-pequeno">
        Por segurança, o TiCuida não encaminha casos de emergência pela fila online.
      </p>
    </div>
  </article>
</template>
