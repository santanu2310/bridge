<script setup lang="ts">
	import { useFriendStore } from "@/stores/friend";
	import { useMessageStore } from "@/stores/message";

	const messageStore = useMessageStore();
	const friendStore = useFriendStore();

	const props = defineProps<{
		id: string;
		imgUrl: string | null;
		displayName: string;
	}>();

	function setCurrentConversation() {
		messageStore.currentConversation = {
			recieverId: props.id,
			convId: null,
		};
		console.log(props.id);
	}

	function getInitials(name: string) {
		return name
			.split(" ")
			.map((word) => word.charAt(0).toUpperCase())
			.join("");
	}

	function setAsCurrentConversation() {
		friendStore.getConversations(props.id);
	}
</script>

<template>
	<div
		class="w-full h-7 flex items-center cursor-pointer"
		@click="setCurrentConversation()"
	>
		<div
			class="w-auto h-full aspect-square flex items-center justify-center"
		>
			<div class="w-full h-full overflow-hidden rounded-full">
				<img
					v-if="imgUrl"
					:src="imgUrl"
					alt=""
					class="w-full h-full object-cover"
				/>
				<div
					v-else
					class="w-full h-full flex items-center justify-center bg-red-500"
				>
					<span class="w-fit h-fit block text-white text-xs">{{
						getInitials(displayName)
					}}</span>
				</div>
			</div>
		</div>
		<div class="h-full flex items-center flex-grow">
			<div class="p-2 flex flex-grow">
				<span class="text-color-heading text-sm font-medium">{{
					displayName
				}}</span>
			</div>
			<div class="h-full">
				<div
					class="h-4/5 aspect-square flex items-center justify-center"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="currentColor"
						class="w-1/2"
					>
						<path
							d="M12 3C10.9 3 10 3.9 10 5C10 6.1 10.9 7 12 7C13.1 7 14 6.1 14 5C14 3.9 13.1 3 12 3ZM12 17C10.9 17 10 17.9 10 19C10 20.1 10.9 21 12 21C13.1 21 14 20.1 14 19C14 17.9 13.1 17 12 17ZM12 10C10.9 10 10 10.9 10 12C10 13.1 10.9 14 12 14C13.1 14 14 13.1 14 12C14 10.9 13.1 10 12 10Z"
						></path>
					</svg>
				</div>
			</div>
		</div>
	</div>
</template>
