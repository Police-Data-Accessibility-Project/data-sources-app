<template>
  <AppHeader />
  <router-view></router-view>
  <AppFooter />
</template>

<script>
import AppHeader from './components/AppHeader.vue';
import AppFooter from './components/AppFooter.vue';

export default {
  name: 'App',
  components: {
    AppHeader,
    AppFooter
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
