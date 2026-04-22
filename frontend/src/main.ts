import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';

// Make sure your CSS (which contains Tailwind) is imported
import './style.css'; 

const app = createApp(App);
const pinia = createPinia();

app.use(pinia); // <--- This is the crucial missing line!
app.mount('#app');