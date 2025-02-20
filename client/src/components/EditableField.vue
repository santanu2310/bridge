<script setup lang="ts">
	import { ref } from "vue";
	import type { Ref } from "vue";
	import axios from "axios";

	import IconPencil from "./icons/IconPencil.vue";

	const props = defineProps<{
		d_key: string;
		d_value: string;
		label: string;
	}>();

	const userData = ref(props.d_value);
	const isReadonly = ref(true);
	const dataElement = ref<HTMLInputElement | null>(null);

	async function handleUpdate() {
		if (isReadonly.value) {
			isReadonly.value = false;
			dataElement.value?.focus();
		} else {
			isReadonly.value = true;
			try {
				const response = await axios({
					method: "patch",
					url: "http://localhost:8000/users/update",
					data: {
						[props.d_key]: userData.value,
					},
					withCredentials: true,
				});
			} catch (error) {}
		}
	}
</script>

<template>
	<div class="w-full h-auto">
		<span class="text-sm font-light leading-4">{{ props.label }}</span>
		<div class="w-full p-x-8 flex items-center">
			<input
				type="text"
				class="h-7 text-color-heading bg-color-background outline-none duration-200 border-b-2 text-sm font-medium border-color-background focus:border-primary"
				style="width: calc(100% - 2.25rem)"
				:readonly="isReadonly"
				ref="dataElement"
				v-model="userData"
			/>
			<button
				v-if="isReadonly"
				class="w-auto h-8 aspect-square flex items-center justify-center rounded-lg bg-color-background-soft"
				@click="handleUpdate()"
			>
				<IconPencil />
			</button>
			<button
				v-else
				class="w-auto h-8 aspect-square flex items-center justify-center rounded-lg bg-transparent"
				@click="handleUpdate()"
			>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					fill="currentColor"
					width="50%"
					height="50%"
				>
					<path
						d="M9.9997 15.1709L19.1921 5.97852L20.6063 7.39273L9.9997 17.9993L3.63574 11.6354L5.04996 10.2212L9.9997 15.1709Z"
					></path>
				</svg>
			</button>
		</div>
	</div>
</template>
