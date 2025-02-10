<script setup lang="ts">
	import { ref, onMounted } from "vue";

	import IconLogo from "@/components/icons/IconLogo.vue";
	import IconMessages from "@/components/icons/IconMessages.vue";
	import IconGroupes from "@/components/icons/IconGroupes.vue";
	import IconFriends from "@/components/icons/IconFriends.vue";
	import IconBell from "@/components/icons/IconBell.vue";

	import Chats from "@/containers/Chats.vue";
	import Friends from "@/containers/Friends.vue";
	import Profile from "@/containers/Profile.vue";
	import Notification from "@/containers/Notification.vue";
	import Settings from "@/containers/Settings.vue";
	import Conversation from "@/containers/Conversation.vue";

	import { useUserStore } from "@/stores/user";
	import { useMessageStore } from "@/stores/message";
	import { useSyncStore } from "@/stores/background_sync";
	import { useFriendStore } from "@/stores/friend";

	const userStore = useUserStore();
	const messageStore = useMessageStore();
	const friendStore = useFriendStore();
	const syncStore = useSyncStore();

	const leftContent = ref<string>("message");

	function switchContainer(n: string) {
		leftContent.value = n;
	}

	onMounted(async () => {
		await userStore.getUser();
		await syncStore.syncAndLoadConversationsFromLastDate();
		await syncStore.syncMessageStatus();
		await friendStore.listFriend();
		await friendStore.getInitialOnlineStatus();
	});
</script>

<template>
	<main class="w-full min-h-full flex">
		<div class="navigation w-16 h-full flex flex-col justify-between">
			<div class="w-full h-fit flex flex-col items-end">
				<div
					class="logo w-full h-auto aspect-square flex items-center justify-center"
				>
					<IconLogo />
				</div>
				<div
					class="w-full h-auto aspect-icon mt-2 flex items-center justify-center cursor-pointer"
					@click="leftContent = 'chats'"
				>
					<IconMessages :size="35" />
				</div>
				<div
					class="w-full h-auto aspect-icon mt-2 flex items-center justify-center cursor-pointer"
				>
					<IconGroupes :size="35" />
				</div>
				<div
					class="w-full h-auto aspect-icon mt-2 flex items-center justify-center cursor-pointer"
					@click="leftContent = 'friends'"
				>
					<IconFriends :size="35" />
				</div>
			</div>
			<div class="w-full h-auto aspect-square flex flex-col items-center">
				<div
					class="w-full h-auto aspect-icon mt-2 flex items-center justify-center cursor-pointer"
					@click="leftContent = 'notification'"
				>
					<IconBell :size="35" />
				</div>
				<div
					class="w-1/2 h-auto aspect-square mt-3 mb-4 overflow-hidden object-cover rounded-full cursor-pointer"
					@click="leftContent = 'profile'"
				>
					<img
						src="https://doot-dark.react.themesbrand.com/static/media/avatar-1.9c8e605558cece65b06c.jpg"
						alt=""
						class="w-full h-full"
					/>
				</div>
			</div>
		</div>
		<div class="left-sidebar w-96 h-full">
			<Chats v-if="leftContent == 'chats'" />
			<Friends v-if="leftContent == 'friends'" />
			<Profile
				v-if="leftContent == 'profile'"
				@switch-container="switchContainer"
			/>
			<Notification v-if="leftContent == 'notification'" />
			<Settings v-if="leftContent == 'settings'" />
		</div>
		<div class="message">
			<Conversation v-if="userStore.currentConversation" />
		</div>
	</main>
</template>

<style scoped>
	.logo {
		color: var(--primary);
	}

	.navigation {
		background: var(--color-background-soft);
	}

	.aspect-icon {
		aspect-ratio: 7/6;
	}

	.message {
		width: calc(100% - 20rem);
		background-color: var(--color-background-soft);
		background-image: url(../assets/background.png);
	}
</style>
