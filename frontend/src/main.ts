import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import Login from './views/Login.vue';
import './style.css'; 

const pinia = createPinia();
const token = localStorage.getItem('auth_token');

const rootComponent = token ? App : Login;

const app = createApp(rootComponent);
app.use(pinia);
app.mount('#app');