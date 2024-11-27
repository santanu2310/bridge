import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import { useAuthStore } from "@/stores/auth";
import { createPinia } from "pinia";
import { createApp } from "vue";
import App from "../App.vue";

const pinia = createPinia();
const app = createApp(App);
app.use(pinia);

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: "/login",
			name: "login",
			component: () => import("../views/LoginView.vue"),
			beforeEnter: () => {
				const authStore = useAuthStore();
				if (authStore.isAuthenticated == true) {
					return { name: "home" };
				}
			},
		},
		{
			path: "/register",
			name: "register",
			component: () => import("../views/RegisterView.vue"),
		},
		{
			path: "/",
			name: "home",
			component: HomeView,
			beforeEnter: async (to, from) => {
				const authStore = useAuthStore();
				while (authStore.isLoading) {
					await new Promise((resolve) => setTimeout(resolve, 100)); // Adjust the delay as needed
				}

				if (authStore.isAuthenticated == false) {
					return { name: "login" };
				}
			},
		},
		{
			path: "/about",
			name: "about",
			// route level code-splitting
			// this generates a separate chunk (About.[hash].js) for this route
			// which is lazy-loaded when the route is visited.
			component: () => import("../views/AboutView.vue"),
		},
	],
});

export default router;
