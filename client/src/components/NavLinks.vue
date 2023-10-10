<template>
  <div class="nav-links-container">
    <img src="@/assets/logo.svg" class="logo" @click="navHome()"/>
    <div class="nav-links small">
      <a href="https://airtable.com/shrbFfWk6fjzGnNsk" target="_blank" rel="noopener noreferrer">Request data</a>
      <p>|</p>
      <a href="https://airtable.com/shrJafakrcmTxHU2i" target="_blank" rel="noopener noreferrer">Submit a Data Source</a>
      <p>|</p>
      <a href="https://docs.pdap.io/" target="_blank" rel="noopener noreferrer">Docs</a>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NavLinks',
  navHome() {
      this.$router.push('/')
    }
}
</script>

<style>
.nav-links-container {
  display: flex;
  justify-content: space-between;
}

.nav-links {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.nav-links a, .nav-links p {
  margin: 0 .5rem;
}
</style>