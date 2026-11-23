<script setup>
import redesSociais from '../assets/figma/redes-sociais.svg'
</script>

<template>
  <footer class="rodape">
    <ul class="rodape-links">
      <li><RouterLink to="/#sobre">SOBRE NÓS</RouterLink></li>
      <li><RouterLink to="/sobre#contato">CONTATO</RouterLink></li>
      <li><RouterLink to="/sobre#termos">TERMOS E CONDIÇÕES</RouterLink></li>
      <li><RouterLink to="/sobre#cookies">POLÍTICA DE COOKIES</RouterLink></li>
    </ul>
    <img class="rodape-redes" :src="redesSociais" alt="" aria-hidden="true" />
    <p class="rodape-aviso">
      O Ti Cuida é uma pré-triagem e <strong>não substitui atendimento médico</strong>. Em emergência, ligue
      <a href="tel:192">192 (SAMU)</a>. Projeto acadêmico – Programação Web Avançada – UVV. Dados de demonstração
      fictícios.
    </p>
  </footer>
</template>
