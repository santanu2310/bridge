<script setup lang="ts">
	import { useFriendStore } from "@/stores/friend";
	import Notification from "@/components/Notification.vue";
	import IconBack from "@/components/icons/IconBack.vue";

	const emit = defineEmits(["friends"]);
	const friendStore = useFriendStore();
</script>

<template>
	<div class="max-h-svh flex flex-col">
		<div
			class="w-full h-12 mt-4 p-6 flex items-center justify-center relative"
		>
			<button
				class="h-full aspect-square absolute left-3"
				@click="emit('friends')"
			>
				<IconBack />
			</button>
			<span class="font-medium text-xl">Friend Requests</span>
		</div>
		<div class="w-full h-auto overflow-auto flex flex-col flex-grow">
			<div class="" v-for="requests in friendStore.friendRequests">
				<Notification
					:id="requests.id"
					:name="requests.user.full_name"
					:message="requests.message ? requests.message : ''"
				/>
			</div>
		</div>
	</div>
</template>

<style scoped></style>
