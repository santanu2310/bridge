import { defineStore } from "pinia";
import { reactive } from "vue";
import axios from "axios";
import { useAuthStore } from "@/stores/auth";
import type { User } from "@/types/User";

export const useUserStore = defineStore("user", () => {
	const authStore = useAuthStore();

	const user = reactive<User>({
		id: "",
		userName: "",
		fullName: "",
		email: "",
		bio: "",
		profilePicUrl: "",
		joinedDate: "",
	});

	const friends = reactive<User[]>([]);

	async function getUser() {
		try {
			const response = await axios({
				method: "get",
				url: "http://localhost:8000/user/me",
				withCredentials: true,
			});

			if (response.status === 200) {
				user.id = response.data._id;
				user.userName = response.data.username;
				user.fullName = response.data.full_name;
				user.email = response.data.email;
				user.bio = response.data.bio;
				user.profilePicUrl = response.data.profile_picture;
				user.joinedDate = response.data.created_at;
			}
		} catch (error) {
			authStore.getTokenPair();
			console.error(error);
		}
	}

	// async function listFriends() {
	// 	try {
	// 		const response = await axios({
	// 			method: "get",
	// 			url: "http://localhost:8000/friends/get-friends",
	// 			withCredentials: true,
	// 		});

	// 		if (response.status === 200) {
	// 			console.log(response.data);
	// 		}
	// 	} catch (error) {
	// 		console.error(error);
	// 	}
	// }

	return { user, getUser };
});
