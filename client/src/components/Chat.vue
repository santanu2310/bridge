<script setup lang="ts">
	import { onMounted, ref } from "vue";
	import type { User } from "@/types/User";
	import type { Message } from "@/types/Message";
	import { indexedDbService } from "@/services/indexDbServices";
	import { getInitials } from "@/utils/StringUtils";
	import { useUserStore } from "@/stores/user";
	import { formatDateDifference } from "@/utils/DateUtils";

	const userStore = useUserStore();
	const isOnline = userStore.useOnlineStatusManager().isOnline;

	// Define props for component
	const props = defineProps<{
		id: string;
		userId: string;
		lastMessageDate: string;
		messages: Message[];
	}>();

	// reactive state to hold user value
	const user = ref<User | null>(null);

	// Calculate unseen messages count on component initialization
	const unseenMessagesCount = props.messages.filter(
		(message) => message.status != "seen"
	).length;

	// Fetch user data on component mount
	onMounted(async () => {
		user.value = (await indexedDbService.getRecord(
			"friends",
			props.userId
		)) as User;
	});

	// Function to set current conversation in user store
	async function setCurrentConversation() {
		userStore.currentConversation = {
			receiverId: props.userId,
			convId: props.id,
		};
	}
</script>

<template>
	<div
		class="w-full h-auto flex items-center cursor-pointer"
		@click="setCurrentConversation()"
		v-if="user"
	>
		<div
			class="w-auto h-7 aspect-square flex items-center justify-center relative"
		>
			<div class="w-full h-full overflow-hidden rounded-full">
				<img
					v-if="user?.profilePicUrl"
					:src="user?.profilePicUrl"
					alt=""
					class="w-full h-full object-cover"
				/>
				<div
					v-else
					class="w-full h-full flex items-center justify-center bg-red-500"
				>
					<span class="w-fit h-fit block text-white text-xs">{{
						getInitials(user.fullName || (user.userName as string))
					}}</span>
				</div>
			</div>
			<div
				v-if="isOnline(props.userId)"
				class="w-3 h-auto aspect-square rounded-full absolute bg-color-background"
				style="padding: 2px; bottom: -2px; right: -2px"
			>
				<span
					class="w-full h-full aspect-square block rounded-full bg-green-400"
				></span>
			</div>
		</div>
		<div class="h-full flex items-center justify-between flex-grow">
			<div class="p-2 flex">
				<span class="text-color-heading text-sm font-medium">{{
					user.fullName || (user.userName as string)
				}}</span>
			</div>
			<div class="flex flex-col justify-end items-center">
				<span
					class="text-xs text-color-heading font-semibold"
					v-if="unseenMessagesCount > 0"
					>{{ unseenMessagesCount }}</span
				>
				<span class="text-xs font-light">{{
					formatDateDifference(props.lastMessageDate)
				}}</span>
			</div>
		</div>
	</div>
</template>
