<script setup lang="ts">
	import { ref } from "vue";
	import { FileStatus } from "@/types/Commons";
	import type { Message, FileInfo } from "@/types/Message";
	import { FileType } from "@/types/Message";
	import { formatFileSize } from "@/utils/StringUtils";
	import IconDownload from "@/components/icons/IconDownload.vue";
	import IconAdd from "@/components/icons/IconAdd.vue";
	import IconClock from "@/components/icons/IconClock.vue";
	import IconDoubleTick from "@/components/icons/IconDoubleTick.vue";
	import IconUpload from "@/components/icons/IconUpload.vue";
	import IconBuffer from "@/components/icons/IconBuffer.vue";
	import IconLoading from "@/components/icons/IconLoading.vue";

	const fileInfo: FileInfo = {
		type: FileType.attachment,
		key: null,
		tempFileId: null,
		size: 20201,
		name: "Bridge_Document_20250228.pdf",
	};
	const message: Message = {
		id: "67b3234a740cd00a05e69a98",
		conversationId: "67b3234a740cd00a05e69a98",
		senderId: "67b3234a740cd00a05e69a98",
		receiverId: null,
		message: "Hello",
		attachment: fileInfo,
		sendingTime: "2025-02-23T12:34:56Z",
		receivedTime: null,
		seenTime: null,
		status: "pending",
	};
	const messageDate = new Date(message.sendingTime as string);
	const fileState = ref<FileStatus>(FileStatus.uploading);
</script>

<template>
	<div class="min-h-svh bg-color-background-mute">
		<div class="w-fit h-fit p-1 bg-color-background rounded-md">
			<div
				class="min-w-56 max-w-80 w-fit p-2 flex items-center"
				v-if="message.attachment"
			>
				<div class="h-fit flex flex-grow">
					<div
						class="h-11 aspect-square flex items-center justify-center rounded-full bg-color-background-mute"
					>
						<IconAdd :size="60" />
					</div>
					<div class="ml-2 flex flex-grow flex-col">
						<span class="w-auto text-sm font-normal break-all">{{
							message.attachment.name
						}}</span>
						<span class="mt-1 text-xxs font-extralight">{{
							formatFileSize(message.attachment.size!)
						}}</span>
					</div>
				</div>
				<!-- area modified -->
				<button
					class="h-10 aspect-square ml-3 flex justify-center items-center"
					@click="console.log('downloadFile')"
					v-if="message.status != 'pending'"
				>
					<IconDownload />
				</button>
				<div class="" v-else>
					<button
						class="h-10 aspect-square ml-3 flex justify-center items-center"
						@click="console.log('UPloadFile')"
						v-if="fileState == FileStatus.unsucessfull"
					>
						<IconUpload />
					</button>
					<button
						class="h-10 aspect-square ml-3 flex justify-center items-center"
						@click="console.log('postProcessing')"
						v-else-if="fileState == FileStatus.uploading"
					>
						<IconLoading :progress="80" />
					</button>
					<button
						class="h-10 aspect-square ml-3 flex justify-center items-center"
						@click="console.log('preProcessing/uploading')"
						v-else
					>
						<IconBuffer />
					</button>
				</div>
			</div>
			<div class="w-full flex flex-nowrap items-end">
				<div class="w-auto mx-1 flex-grow">
					<span
						class="w-auto text-base text-color-heading break-words"
						>{{ message.message }}</span
					>
				</div>
				<div class="w-auto h-fit mt-2 ml-2 leading-4">
					<span class="text-xxs font-thin">
						{{ messageDate.getHours() }}:{{
							messageDate.getMinutes().toString().padStart(2, "0")
						}}
					</span>
				</div>
				<div
					class="w-auto h-4 aspect-square ml-1 mt-3"
					v-if="message.senderId == '67b3234a740cd00a05e69a98'"
				>
					<IconClock v-if="message.status == 'pending'" :size="90" />
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="currentColor"
						v-else-if="message.status == 'send'"
					>
						<path
							d="M9.9997 15.1709L19.1921 5.97852L20.6063 7.39273L9.9997 17.9993L3.63574 11.6354L5.04996 10.2212L9.9997 15.1709Z"
						></path>
					</svg>
					<IconDoubleTick
						:size="100"
						:blue="message.status === 'seen'"
						v-else
					/>
				</div>
			</div>
		</div>
	</div>
</template>

<style>
	@media (min-width: 1024px) {
		.about {
			min-height: 100vh;
			display: flex;
			align-items: center;
		}
	}
</style>
