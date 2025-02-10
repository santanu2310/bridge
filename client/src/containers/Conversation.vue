<script setup lang="ts">
	import { computed, ref, onMounted } from "vue";

	import EmojiPicker from "vue3-emoji-picker";
	import "vue3-emoji-picker/css";

	import { formatDateDifference } from "@/utils/DateUtils";
	import { indexedDbService } from "@/services/indexDbServices";
	import type { User } from "@/types/User";

	import { useMessageStore } from "@/stores/message";
	import { useUserStore } from "@/stores/user";

	import IconSearch from "@/components/icons/IconSearch.vue";
	import IconCall from "@/components/icons/IconCall.vue";
	import IconVideoCall from "@/components/icons/IconVideoCall.vue";
	import IconAbout from "@/components/icons/IconAbout.vue";
	import IconAdd from "@/components/icons/IconAdd.vue";
	import IconSticker from "@/components/icons/IconSticker.vue";
	import IconMic from "@/components/icons/IconMic.vue";
	import IconSend from "@/components/icons/IconSend.vue";
	import IconClose from "@/components/icons/IconClose.vue";
	import Message from "@/components/Message.vue";

	const messageStore = useMessageStore();
	const userStore = useUserStore();
	const friend = ref<User | null>(null);

	onMounted(async () => {
		friend.value = (await indexedDbService.getRecord(
			"friends",
			userStore.currentConversation?.receiverId as string
		)) as User;
	});

	const text = ref<string>("");
	const selectedFile = ref<File | null>(null);

	const inputReference = ref<HTMLInputElement | null>(null);
	const showEmojiBoard = ref(false);
	const myId = userStore.user.id;

	const handleFileUpload = (event: Event) => {
		const file = inputReference.value?.files![0];
		if (file) {
			if (file.size > 10 * 1024 * 1024) {
				alert("File size exceeds 10MB. Please select a smaller file.");
				inputReference.value = null;
			} else {
				selectedFile.value = file;
				inputReference.value = null;
				console.log("Selected file:", file);
				console.log(URL.createObjectURL(file));
			}
		}
	};

	const removeSelectedFile = () => {
		selectedFile.value = null;
		inputReference.value = null;
	};

	// Add a new property "showDate" == true if the day changes
	const messages = computed(() => {
		const rawMessages =
			userStore.conversations[
				userStore.currentConversation?.convId as string
			]?.messages || [];

		let lastDate = 0;

		return rawMessages.map((msg) => {
			const sendingTime = Math.trunc(
				new Date(msg.sendingTime as string).getTime() /
					(1000 * 60 * 60 * 24)
			);
			const showDate = lastDate !== sendingTime;
			lastDate = sendingTime;

			return { ...msg, showDate };
		});
	});

	function onSelectEmoji(emoji: object) {
		text.value = text.value + (emoji as { i: string }).i;
		console.log((emoji as { i: string }).i);
	}

	function getInitials(name: string) {
		const sArray = name
			.split(" ")
			.map((word) => word.charAt(0).toUpperCase());
		return sArray[0] + sArray[sArray.length - 1];
	}

	async function sendMessage() {
		if (selectedFile.value) {
			messageStore.sendMessageWithFile(
				selectedFile.value,
				text.value,
				userStore.currentConversation!.receiverId,
				userStore.currentConversation!.convId
			);
		} else {
			if (text.value != "") {
				messageStore.sendMessage(text.value);
				text.value = "";
			}
		}
	}
</script>
<template>
	<div class="w-full h-full flex flex-col">
		<div
			class="w-full h-20 px-2 flex items-center justify-between bg-color-background-mute"
		>
			<div class="h-fit py-4 mx-4 flex items-center" v-if="friend">
				<div class="h-10 overflow-hidden aspect-square rounded-full">
					<img
						v-if="friend.profilePicUrl"
						:src="friend.profilePicUrl"
						alt=""
						class="w-full h-full object-cover"
					/>
					<div
						v-else
						class="w-full h-full flex items-center justify-center bg-red-500"
					>
						<span
							class="w-fit h-fit block text-white text-sm font-semibold"
							>{{
								getInitials(
									friend.fullName ||
										(friend.userName as string)
								)
							}}</span
						>
					</div>
				</div>
				<div class="h-fit ml-3 flex flex-col">
					<span class="text-base font-medium">{{
						friend.fullName || friend.userName
					}}</span>
					<span class="text-xs text-color-heading">online</span>
				</div>
			</div>
			<div class="h-fit flex items-center">
				<button
					class="h-8 mx-2 aspect-square bg-transparent border-none flex items-center justify-center"
				>
					<IconSearch />
				</button>
				<button
					class="h-8 mx-2 aspect-square bg-transparent border-none flex items-center justify-center"
				>
					<IconCall />
				</button>
				<button
					class="h-8 mx-2 aspect-square bg-transparent border-none flex items-center justify-center"
				>
					<IconVideoCall />
				</button>
				<button
					class="h-8 mx-2 aspect-square bg-transparent border-none flex items-center justify-center"
				>
					<IconAbout />
				</button>
				<button
					class="h-8 mx-2 aspect-square bg-transparent border-none flex items-center justify-center"
				>
					<IconMore />
				</button>
			</div>
		</div>
		<div class="w-full px-3 overflow-auto flex-grow">
			<div class="flex flex-col justify-end">
				<div
					class="w-full h-fit p-2 flex flex-col"
					v-for="msg in messages"
					:class="{ 'items-end': msg.senderId == myId }"
				>
					<div
						class="w-full h-fit mb-3 flex justify-center"
						v-if="msg.showDate"
					>
						<span
							class="w-auto h-fit p-2 text-sm font-light text-color-heading rounded-lg bg-color-background-mute"
							>{{
								formatDateDifference(
									msg.sendingTime as string,
									false
								)
							}}
						</span>
					</div>
					<Message
						:message="msg"
						:user-id="userStore.user.id as string"
					/>
				</div>
			</div>
		</div>

		<div
			class="w-full h-20 p-2 flex items-center bg-color-background-mute relative"
		>
			<label
				for="attachment"
				class="h-8 mx-2 aspect-square bg-transparent border-none flex items-center justify-center rounded-full hover:bg-color-background-soft"
			>
				<IconAdd :size="66" :rotate="90" />
			</label>
			<input
				type="file"
				name="attachment"
				id="attachment"
				hidden
				ref="inputReference"
				max="20971520"
				@change="handleFileUpload"
			/>
			<button
				class="h-8 mx-2 aspect-square bg-transparent border-none flex items-center justify-center"
				@click="
					showEmojiBoard
						? (showEmojiBoard = false)
						: (showEmojiBoard = true)
				"
			>
				<IconSticker :size="66" />
			</button>
			<div
				class="h-10 mx-2 px-1 flex items-center flex-grow bg-color-background-soft rounded-lg"
			>
				<div
					class="w-fit max-w-52 h-8 pl-3 pr-2 rounded-2xl bg-color-background flex items-center flex-nowrap"
					v-if="selectedFile"
				>
					<span class="text-color-heading font-medium text-xs">{{
						selectedFile.name
					}}</span>
					<button
						class="h-3/5 w-auto aspect-square ml-2 rounded-full border-2 border-color-heading flex items-center justify-center"
						@click="removeSelectedFile"
					>
						<IconClose :size="70" />
					</button>
				</div>
				<input
					class="h-full px-3 flex-grow text-sm text-color-heading bg-transparent rounded-lg border-none outline-none"
					type="text"
					v-model="text"
					placeholder="Type your message ..."
					@keyup.enter="sendMessage()"
				/>
			</div>
			<button
				class="h-8 mx-2 aspect-square bg-transparent border-none flex items-center justify-center"
			>
				<IconMic :size="64" />
			</button>
			<button
				class="h-10 mx-2 w-12 border-none flex items-center justify-center bg-primary rounded-lg"
				@click="sendMessage()"
			>
				<IconSend :size="60" />
			</button>
			<div
				class="emoji-board w-72 h-auto absolute left-5 bottom-24"
				v-if="showEmojiBoard"
			>
				<EmojiPicker
					:native="true"
					@select="onSelectEmoji"
					theme="auto"
				/>
			</div>
		</div>
	</div>
</template>

<style>
	.emoji-board * {
		background: var(--color-background-mute) !important;
	}

	.v3-groups {
		filter: none !important;
	}

	.v3-groups > button > span > img {
		filter: invert(1);
		background: transparent !important;
	}
</style>
