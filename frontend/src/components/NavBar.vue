<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import iconeAjuda from '../assets/figma/icone-ajuda.png'
import iconeUsuario from '../assets/figma/icone-usuario.png'
import logo from '../assets/figma/logo.png'
import { encerrarSessao, sessao } from '../stores/sessao'

const router = useRouter()
const route = useRoute()
const aberto = ref(false)
const menu = ref(null)

const papel = computed(() => sessao.usuario?.papel)
const nome = computed(() => {
  if (papel.value === 'paciente') return sessao.usuario?.paciente?.nome?.split(' ')[0]
  if (papel.value === 'operador') return sessao.usuario?.unidade?.nome
  return ''
})

watch(() => route.fullPath, () => (aberto.value = false))

function clicarUsuario() {
  if (!sessao.token) return router.push('/login')
  aberto.value = !aberto.value
}

function fecharAoClicarFora(evento) {
  if (aberto.value && menu.value && !menu.value.contains(evento.target)) aberto.value = false
}

onMounted(() => document.addEventListener('click', fecharAoClicarFora))
onBeforeUnmount(() => document.removeEventListener('click', fecharAoClicarFora))

function sair() {
  encerrarSessao()
  router.push('/login')
}
</script>

<template>
  <header class="cabecalho">
    <nav class="cabecalho-conteudo" aria-label="Navegação principal">
      <RouterLink class="marca" to="/" aria-label="Ti Cuida – página inicial">
        <img :src="logo" alt="" />
        <span>Ti Cuida</span>
      </RouterLink>

      <div class="cabecalho-acoes">
        <RouterLink class="icone-cabecalho" to="/sobre" aria-label="Ajuda e perguntas frequentes">
          <img :src="iconeAjuda" alt="" />
        </RouterLink>

        <div ref="menu" class="menu-usuario">
          <button
            class="icone-cabecalho"
            type="button"
            :aria-label="sessao.token ? 'Menu da conta' : 'Entrar'"
            :aria-expanded="sessao.token ? aberto : undefined"
            @click="clicarUsuario"
          >
            <img :src="iconeUsuario" alt="" />
          </button>

          <div v-if="aberto && sessao.token" class="menu-usuario-lista">
            <p class="nome">{{ nome }}</p>
            <template v-if="papel === 'paciente'">
              <RouterLink to="/triagem">Nova triagem</RouterLink>
              <RouterLink to="/meus-atendimentos">Meus atendimentos</RouterLink>
              <RouterLink to="/perfil">Meu perfil</RouterLink>
            </template>
            <RouterLink v-if="papel === 'operador'" to="/unidade">Fila da unidade</RouterLink>
            <button type="button" @click="sair">Sair</button>
          </div>
        </div>
      </div>
    </nav>
  </header>
</template>
