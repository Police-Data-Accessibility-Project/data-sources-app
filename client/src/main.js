import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import axios from 'axios';
import { BASE_URL } from '../globals';

const app = createApp(App);

axios.interceptors.request.use((config) => {
	const pdap = config.url.includes(BASE_URL);
	if (pdap) {
		// Set a dummy value for the Authorization header
		config.headers[
			'AUTHORIZATION'
		] = `Bearer ${process.env.VUE_APP_PDAP_API_KEY}`;
	} else {
		// Delete the Authorization header for other requests
		delete config.headers['Authorization'];
	}
	return config;
});

app.config.globalProperties.$http = axios;

app.use(router).mount('#app');
