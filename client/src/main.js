import './main.css';
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import piniaPersistState from 'pinia-plugin-persistedstate';

import App from './App.vue';
import router from './router';

import 'pdap-design-system/styles';

const pinia = createPinia();
pinia.use(piniaPersistState);
const app = createApp(App);

app.use(pinia);
app.use(router);

app.mount('#app');
