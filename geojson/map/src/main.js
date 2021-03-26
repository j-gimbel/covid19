import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap";

import { createApp } from 'vue'
import App from './App.vue'
import store from './store'

const app = createApp(App)
// Install the store instance as a plugin
app.use(store)
app.mount('#app')