<script setup>
import { computed } from 'vue'
import ilustracao from '../assets/figma/ilustracao.png'
import videoSobre from '../assets/figma/video-sobre.png'
import { sessao } from '../stores/sessao'

const paciente = computed(() => sessao.usuario?.paciente)
</script>

<template>
  <section class="inicio-hero">
    <div class="inicio-hero-conteudo">
      <h1>Clique aqui para iniciar uma triagem!</h1>
      <RouterLink to="/triagem" class="button botao is-grande">Iniciar triagem</RouterLink>
      <p v-if="paciente" class="inicio-hero-links">
        <RouterLink to="/meus-atendimentos">Meus atendimentos</RouterLink>
      </p>
      <p v-else class="inicio-hero-links">
        Novo por aqui? <RouterLink to="/cadastro">Cadastre-se!</RouterLink>
      </p>
      <img class="inicio-ilustracao" :src="ilustracao" alt="" />
    </div>
  </section>

  <section id="sobre" class="sobre-nos">
    <div class="sobre-nos-conteudo">
      <h2>SOBRE NÓS</h2>
      <img :src="videoSobre" alt="Ti Cuida – conheça nossa solução" />
      <p>
        O Ti Cuida nasceu ao observarmos o desafio da superlotação em centros médicos e a dificuldade hospitalar em
        aprimorar as primeiras etapas do atendimento. Com o objetivo de apresentar uma solução na InovaWeek, semana
        de inovação da UVV, formamos um grupo com 9 estudantes de Ciência da Computação e Medicina.
      </p>
      <p>
        Você informa seus sintomas pelo celular, vê quais unidades atendem seu convênio, a lotação de cada uma e a
        distância até você. Ao confirmar, a unidade já recebe seus dados.
      </p>
    </div>
  </section>
</template>
