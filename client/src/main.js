import './main.css';
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import piniaPersistState from 'pinia-plugin-persistedstate';
import { DataLoaderPlugin } from 'unplugin-vue-router/data-loaders';
import Vue3Toastify from 'vue3-toastify';
import 'vue3-toastify/dist/index.css';
import App from './App.vue';
import router from './router';
import 'pdap-design-system/styles';
import { DataLoaderErrorPassThrough } from '@/util/errors';

// TODO: make router available in store?
// pinia.use(({ store }) => {
// 	store.router = markRaw(router);
// });

const app = createApp(App);
const pinia = createPinia();
pinia.use(piniaPersistState);
app.use(pinia);
app.use(DataLoaderPlugin, { router, errors: [DataLoaderErrorPassThrough] });
app.use(router);
app.use(Vue3Toastify, {
	autoClose: 5000,
	containerClassName: 'pdap-toast-container',
	toastClassName: 'pdap-toast',
	style: {
		opacity: 0.95,
	},
	theme: 'auto',
});

app.mount('#app');
