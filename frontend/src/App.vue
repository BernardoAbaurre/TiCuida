<script setup>
import NavBar from './components/NavBar.vue'
import RodapeSite from './components/RodapeSite.vue'
</script>

<template>
  <NavBar />
  <main>
    <RouterView />
  </main>
  <RodapeSite />
</template>
