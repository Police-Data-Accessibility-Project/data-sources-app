<template>
  <NavLinks v-if="showNavLinks()" />
  <NavLogo v-else />
  <router-view></router-view>
  <FooterComponent />
</template>

<script>
import FooterComponent from './components/FooterComponent.vue';
import NavLogo from './components/NavLogo.vue'
import NavLinks from './components/NavLinks.vue'

export default {
  name: 'App',
  components: {
    NavLogo,
    NavLinks,
    FooterComponent
  },
  methods: {
    showNavLinks() {
      return this.$route.path.includes('/data-sources/')
    }
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
