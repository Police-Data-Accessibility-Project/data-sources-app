<template>
  <NavBarLinks v-if="showNavLinks()" />
  <NavBarLogo v-else />
  <router-view></router-view>
  <FooterComponent />
</template>

<script>
import FooterComponent from './components/FooterComponent.vue';
import NavBarLogo from './components/NavBarLogo.vue'
import NavBarLinks from './components/NavBarLinks.vue'

export default {
  name: 'App',
  components: {
    NavBarLogo,
    NavBarLinks,
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
