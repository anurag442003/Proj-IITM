import { createApp } from 'vue';
import App from './Mad2_App.vue';
import router from './router/Mad2_index';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import VueStarRating from 'vue-star-rating';
import store from './Mad2_store';

const app = createApp(App);

app.config.globalProperties.$axios = axios;
app.config.globalProperties.$jwtDecode = jwtDecode;

app.component('star-rating', VueStarRating.default);

app.use(router);

app.use(store);

app.mount('#app');