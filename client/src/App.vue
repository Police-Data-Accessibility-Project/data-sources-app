<template>
  <img src="@/assets/logo.svg" class="logo"/>
  <router-view></router-view>
  <footer>
    <div class="footer-links small">
      <a href="https://airtable.com/shrbFfWk6fjzGnNsk" target="_blank" rel="noopener noreferrer">Request data</a>
      <p>|</p>
      <a href="https://airtable.com/shrJafakrcmTxHU2i" target="_blank" rel="noopener noreferrer">Submit a Data Source</a>
      <p>|</p>
      <a href="https://docs.pdap.io/" target="_blank" rel="noopener noreferrer">Docs</a>
    </div>
    <p class="small">To report an issue or ask a question, email<a href="mailto:contact@pdap.io">contact@pdap.io</a></p>
  </footer>
</template>

<script>
export default {
  name: 'App'
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

footer {
  position: relative;
  bottom: 0;
  width: 100%;
  padding: 1rem 0;
  text-align: center;
  display:flex;
  flex-direction:column;
  align-items: center;
}

.footer-links {
  display: flex;
  justify-content: center;
  margin-bottom:10px;
}

footer a, footer p {
  margin: 0 .5rem;
  text-decoration: none;
}

.footer-email {
  padding: 1rem 0
}

@media (max-width: 700px) {
  footer a, footer p {
    margin: 0 .25rem;
    font-size: 1rem;
  }
}

@media (max-width: 500px) {
  footer a, footer p {
    margin: 0 .25rem;
    font-size: .75rem;
  }
}
</style>
