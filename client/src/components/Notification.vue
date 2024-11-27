<script setup lang="ts">
	import { ref } from "vue";
	import axios from "axios";

	async function acceptRequest(request_id: string) {
		console.log(request_id);
		try {
			const response = await axios({
				method: "patch",
				url: `http://localhost:8000/friends/accept-request/${request_id}`,
				withCredentials: true,
			});
			console.log(response.status);

			if (response.status === 200) {
				console.log(response.data);
			}
		} catch (error) {
			console.error(error);
		}
	}
	const props = defineProps<{
		id: string;
		name: string;
		message: string;
	}>();
	console.log(props.name);
</script>
<template>
	<div class="w-full p-4 flex">
		<div class="h-16 w-auto aspect-square overflow-hidden rounded-full">
			<img
				src="https://doot-dark.react.themesbrand.com/static/media/avatar-1.9c8e605558cece65b06c.jpg"
				alt=""
				class="w-full h-full object-cover"
			/>
		</div>
		<div
			class="h-auto flex flex-col items-start text-sm"
			style="min-width: calc(97% - 4rem); margin-left: 3%"
		>
			<span class="font-medium"
				>Freind request from <b class="">{{ name }}</b></span
			>
			<span class="font-light">{{ message }}</span>
			<div class="w-full mt-2 flex justify-between">
				<button class="accept-btn" @click="acceptRequest(id)">
					Accept
				</button>
				<button class="reject-btn">Decline</button>
			</div>
		</div>
	</div>
</template>

<style scoped>
	:root{
		--height: `${height}rem`
	}

	.not-info{
		width: calc(100% - var(--height));
	}

	.accept-btn{
		width: 45%;
		height: 28px;
		border-radius: 6px;
		border: 2px solid var(--primary);
		color: var(--primary);
	}

	.accept-btn:hover{
		background: var(--primary);
		color: var(--color-background);
	}

	.reject-btn{
		width: 45%;
		height: 28px;
		border-radius: 6px;
		background: rgb(227, 53, 14);
		color: var(--color-background);
	}
</style>
