<script setup lang="ts">
	import { vElementVisibility } from "@vueuse/components";
	import IconDoubleTick from "./icons/IconDoubleTick.vue";
	import type { Message } from "@/types/Message";
	import { useSyncStore } from "@/stores/background_sync";

	interface Props {
		message: Message;
		userId: string;
	}

	const syncStore = useSyncStore();

	const props = defineProps<Props>();
	const messageDate = new Date(props.message.sendingTime as string);

	function onElementVisibility(state: boolean) {
		// This function will trigger when message is visible in the screen
		if (
			props.message.senderId != props.userId &&
			props.message.status != "seen" &&
			state
		) {
			syncStore.markMessageAsSeen(props.message);
		}
	}
</script>
<template>
	<div
		class="w-fit h-fit p-2 pb-1 flex flex-nowrap items-endArgument of type 'Readonly<ShallowRef<unknown>>' is not assignable to parameter of type 'Element'. Type 'Readonly<ShallowRef<unknown>>' is missing the following properties from type 'Element': attributes, classList, className, clientHeight, and 173 more.ts-plugin(2345) const element: Readonly<ShallowRef<unknown>> bg-color-background rounded-md"
		v-element-visibility="onElementVisibility"
	>
		<div class="w-auto mx-1">
			<span class="max-w-52 text-base text-color-heading break-words">{{
				message.message
			}}</span>
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
			v-if="props.message.senderId == props.userId"
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="currentColor"
				v-if="props.message.status == 'send'"
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
</template>
