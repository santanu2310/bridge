<script setup lang="ts">
	import IconSearch from "@/components/icons/IconSearch.vue";
	import Chat from "@/components/Chat.vue";
	import { useUserStore } from "@/stores/user";

	const userStore = useUserStore();
</script>

<template>
	<div class="w-full h-full px-6 pt-6 flex flex-col">
		<div class="w-full flex justify-between">
			<span class="font-medium text-xl">Chats</span>
		</div>
		<div class="w-full h-10 mt-5 flex">
			<input
				type="text"
				class="w-max h-full px-3 flex-grow rounded-s bg-color-background-mute text-sm outline-none"
			/>
			<button
				class="w-auto h-full flex items-center justify-center aspect-square rounded-e bg-color-background-mute hover:bg-color-background-soft"
			>
				<IconSearch :size="40" />
			</button>
		</div>
		<div class="w-full mt-5 flex-grow overflow-y-scroll">
			<div
				class="w-full h-12 flex flex-col justify-center"
				v-for="(conv, key) in userStore.conversations"
			>
				<Chat
					:id="key as string"
					:userId="conv.participant"
					:last-message-date="conv.lastMessageDate"
					:messages="conv.messages"
				/>
			</div>
		</div>
	</div>
</template>
