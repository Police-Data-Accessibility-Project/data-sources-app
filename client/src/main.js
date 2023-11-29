import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import 'pdap-design-system/styles';

createApp(App).use(router).mount('#app');
