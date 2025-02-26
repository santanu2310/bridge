import { defineStore } from "pinia";
import { reactive, ref, computed } from "vue";
import axios from "axios";
import { useAuthStore } from "@/stores/auth";
import type { User } from "@/types/User";
import type { Message } from "@/types/Message";

export const useUserStore = defineStore("user", () => {
	const authStore = useAuthStore();

	// Reactive object to track conversation
	const conversations = ref<{
		[key: string]: {
			messages: Message[];
			participant: string;
			lastMessageDate: string;
			isActive: boolean;
		};
	}>({});

	// Reactive object to track open chats
	const currentConversation = ref<{
		convId: string | null;
		receiverId: string | null;
	} | null>(null);

	// Reactive object to track user online status
	const userStatuses = ref<Record<string, boolean>>({});

	const user = reactive<User>({
		id: "",
		userName: "",
		fullName: "",
		email: "",
		bio: "",
		location: "",
		profilePicUrl: "",
		joinedDate: "",
	});

	async function getUser() {
		try {
			const response = await authStore.authAxios({
				method: "get",
				url: "users/me",
			});

			console.log(response);

			if (response.status === 200) {
				user.id = response.data.id;
				user.userName = response.data.username;
				user.fullName = response.data.full_name;
				user.email = response.data.email;
				user.bio = response.data.bio;
				user.location = response.data.location;
				user.profilePicUrl = response.data.profile_picture;
				user.joinedDate = response.data.created_at;
			}
		} catch (error) {
			authStore.getTokenPair();
			console.error(error);
		}
	}

	function useOnlineStatusManager() {
		return {
			// Check if user is online
			isOnline: (userId: string) => {
				console.log(userStatuses.value);
				return userStatuses.value[userId] || false;
			},

			// Set a user as online
			setOnline: (userId: string) => {
				userStatuses.value[userId] = true;
			},

			// Set a user as offline
			setOffline: (userId: string) => {
				userStatuses.value[userId] = false;
			},
		};
	}

	return {
		user,
		conversations,
		currentConversation,
		getUser,
		useOnlineStatusManager,
	};
});
