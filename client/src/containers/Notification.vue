<script setup lang="ts">
	import { reactive, ref } from "vue";
	import type { Ref } from "vue";
	import axios, { type AxiosResponse } from "axios";
	import Notification from "@/components/Notification.vue";

	interface User {
		id: string;
		username: string;
		full_name: string;
		email: string;
		profile_picture?: string;
		created_at?: string;
	}

	interface FriendRequest {
		id: string;
		user: User;
		message: string;
		status: string;
		created_time: string;
	}

	const notifications = ref<FriendRequest[]>([]);

	async function getFriendRequests() {
		try {
			const response = await axios({
				method: "get",
				url: "http://localhost:8000/friends/get-requests",
				withCredentials: true,
			});

			if (response.status === 200) {
				notifications.value = response.data;
				console.log(response.data);
			}
		} catch (error) {
			console.error(error);
		}
	}
	getFriendRequests();
</script>

<template>
	<div>
		<div class="w-full p-6 flex items-center justify-between">
			<span class="font-medium text-xl">Notifications</span>
		</div>
		<div class="w-full h-auto">
			<div class="" v-for="notification in notifications">
				<!-- {{ notification.user }} -->
				<Notification
					:id="notification.id"
					:name="notification.user.full_name"
					:message="notification.message"
				/>
			</div>
		</div>
	</div>
</template>

<style scoped></style>
