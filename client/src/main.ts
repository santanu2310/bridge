import "./assets/main.css";

import { createApp } from "vue";
import { createPinia } from "pinia";

import VueCookies from "vue-cookies";

import App from "./App.vue";
import router from "./router";
import "./index.css";

const app = createApp(App);

app.use(router);
app.use(VueCookies);
app.use(createPinia());

app.mount("#app");
