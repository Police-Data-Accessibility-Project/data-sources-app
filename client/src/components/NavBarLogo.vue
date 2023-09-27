<template>
  <img src="@/assets/logo.svg" class="logo" @click="navHome()"/>
</template>

<script>
export default {
  name: 'NavBarLogo',
  methods: {
    navHome() {
      this.$router.push('/')
    }
  }
}
</script>