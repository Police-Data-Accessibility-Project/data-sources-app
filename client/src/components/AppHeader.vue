<template>
  <header>
    <NavLinks v-if="showNavLinks()" />
    <NavLogo v-else />
  </header>
</template>

<script>
import NavLogo from './NavLogo.vue';
import NavLinks from './NavLinks.vue';

export default {
  name: "AppHeader",
  components: {
    NavLogo,
    NavLinks
  },
  methods: {
    showNavLinks() {
      return this.$route.path.includes('/data-sources/')
    }
  }
}
</script>