import { inject, ref } from "vue";
import { defineStore } from "pinia";
import axios from "axios";
import VueCookies from "vue-cookies";

export const useAuthStore = defineStore("authentication", () => {
	const isAuthenticated = ref(false);
	const isLoading = ref(true);
	const $cookies = inject<typeof VueCookies>("$cookies");

	if ($cookies) {
		if ($cookies.get("access_t") != null) {
			isAuthenticated.value = true;
			isLoading.value = false;
		} else {
			getTokenPair();
		}
	}

	async function getTokenPair(): Promise<void> {
		try {
			const response = await axios({
				method: "post",
				url: "http://localhost:8000/user/refresh-token",
				withCredentials: true,
			});
			if (response.status === 200) {
				isAuthenticated.value = true;
				isLoading.value = false;
			}
		} catch (error) {
			isLoading.value = false;
		}
	}
	return { isAuthenticated, isLoading, getTokenPair };
});
