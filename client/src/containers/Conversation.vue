<script setup lang="ts">
	import { ref } from "vue";

	import EmojiPicker from "vue3-emoji-picker";
	import "vue3-emoji-picker/css";

	import { useMessageStore } from "@/stores/message";

	import IconSearch from "@/components/icons/IconSearch.vue";
	import IconCall from "@/components/icons/IconCall.vue";
	import IconVideoCall from "@/components/icons/IconVideoCall.vue";
	import IconAbout from "@/components/icons/IconAbout.vue";
	import IconMore from "@/components/icons/IconMore.vue";
	import IconSticker from "@/components/icons/IconSticker.vue";
	import IconMic from "@/components/icons/IconMic.vue";
	import IconSend from "@/components/icons/IconSend.vue";

	const imgUrl =
		"https://doot-dark.react.themesbrand.com/static/media/avatar-3.6256d30dbaad2b8f4e60.jpg";

	const messageStore = useMessageStore();
	const text = ref<string>("");
	const showEmojiBoard = ref(false);

	function onSelectEmoji(emoji: object) {
		text.value = text.value + (emoji as { i: string }).i;
		console.log((emoji as { i: string }).i);
	}

	function getInitials(name: string) {
		return name
			.split(" ")
			.map((word) => word.charAt(0).toUpperCase())
			.join("");
	}

	async function sendMessage() {
		if (text.value != "") {
			messageStore.sendMessage(text.value);
			text.value = "";
		}
	}
</script>
<template>
	<div class="w-full h-full flex flex-col">
		<div
			class="w-full h-20 px-2 flex items-center justify-between bg-color-background-mute"
		>
			<div class="h-fit mx-4 flex items-center">
				<div class="h-12 overflow-hidden rounded-full">
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
							getInitials("")
						}}</span>
					</div>
				</div>
				<div class="h-fit ml-3 flex flex-col">
					<span class="text-base font-medium">Anita Sing</span>
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
		<div class="w-full flex flex-grow"></div>
		<div
			class="w-full h-20 px-2 flex items-center bg-color-background-mute relative"
		>
			<button
				class="h-8 mx-2 aspect-square bg-transparent border-none flex items-center justify-center"
			>
				<IconMore :size="66" :rotate="90" />
			</button>
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
			<div class="h-10 mx-2 flex flex-grow">
				<input
					class="w-full h-full px-3 text-sm text-color-heading bg-color-background-soft rounded-lg border-none outline-none"
					type="text"
					v-model="text"
					placeholder="Type your message ..."
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
