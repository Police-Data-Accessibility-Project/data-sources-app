<template>
  <NavBar />
  <router-view></router-view>
  <FooterComponent />
</template>

<script>
import FooterComponent from './components/FooterComponent.vue';
import NavBar from './components/NavBar.vue'

export default {
  name: 'App',
  components: {
    NavBar,
    FooterComponent
  }
}
</script>

<style>
#app {
  margin: 0;
  padding: 1rem;
}

.logo {
  width: 50px;
  margin: 1rem
}
</style>
