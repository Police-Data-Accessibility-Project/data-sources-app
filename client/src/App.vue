<template>
  <AppHeader />
  <router-view></router-view>
  <FooterComponent />
</template>

<script>
import AppHeader from './components/AppHeader.vue';
import FooterComponent from './components/FooterComponent.vue';

export default {
  name: 'App',
  components: {
    AppHeader,
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
  margin: 1rem;
  cursor: pointer;
}
</style>
