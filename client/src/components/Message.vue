<script setup lang="ts">
	interface Props {
		msg: string;
		status: string;
		time: string;
		isMyMessage: boolean;
	}

	const props = defineProps<Props>();
	const messageDate = new Date(props.time);
</script>
<template>
	<div
		class="w-fit h-fit p-2 flex flex-nowrap items-end bg-color-background rounded-md"
	>
		<div class="w-auto mx-1">
			<span class="max-w-52 text-base text-color-heading break-words">{{
				msg
			}}</span>
		</div>
		<div class="w-auto h-fit ml-2 leading-4">
			<span class="text-xxs font-thin">
				{{ messageDate.getHours() }}:{{
					messageDate.getMinutes().toString().padStart(2, "0")
				}}
			</span>
		</div>
		<div class="w-auto h-4 aspect-square ml-1" v-if="props.isMyMessage">
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="currentColor"
				v-if="props.status == 'send'"
			>
				<path
					d="M9.9997 15.1709L19.1921 5.97852L20.6063 7.39273L9.9997 17.9993L3.63574 11.6354L5.04996 10.2212L9.9997 15.1709Z"
				></path>
			</svg>

			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 24 24"
				fill="currentColor"
				v-else
			>
				<path
					d="M11.602 13.7599L13.014 15.1719L21.4795 6.7063L22.8938 8.12051L13.014 18.0003L6.65 11.6363L8.06421 10.2221L10.189 12.3469L11.6025 13.7594L11.602 13.7599ZM11.6037 10.9322L16.5563 5.97949L17.9666 7.38977L13.014 12.3424L11.6037 10.9322ZM8.77698 16.5873L7.36396 18.0003L1 11.6363L2.41421 10.2221L3.82723 11.6352L3.82604 11.6363L8.77698 16.5873Z"
				></path>
			</svg>
		</div>
	</div>
</template>
