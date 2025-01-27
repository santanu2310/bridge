<script setup lang="ts">
	import { ref } from "vue";
	import type { Ref } from "vue";
	import axios from "axios";
	import { useFriendStore } from "@/stores/friend";
	import Friend from "@/components/Friend.vue";

	// const userStore = useUserStore();
	// const messageStore = useMessageStore();
	const friendStore = useFriendStore();
	const request_prompt = ref(false);
	const username: Ref<string | null> = ref(null);
	const message: Ref<string | null> = ref(null);

	const currentInitial = ref("");
	function changedInitial(name: string): boolean {
		if (name[0] !== currentInitial.value) {
			currentInitial.value = name[0];
			return true;
		}
		return false;
	}

	async function createFriendRequest() {
		try {
			const response = await axios({
				method: "post",
				url: "http://localhost:8000/friends/make-request",
				data: {
					username: username.value,
					message: message.value,
				},
				withCredentials: true,
			});

			if (response.status === 201) {
				console.log("status 201");
			}
		} catch (error) {
			console.error(error);
		}
	}
</script>

<template>
	<div class="">
		<div class="w-ful p-6 flex items-center justify-between">
			<span class="font-medium text-xl">Friends</span>
			<div class="flex">
				<button
					class="btn-bg w-8 h-8 rounded"
					@click="request_prompt = true"
				>
					+
				</button>
			</div>
		</div>
		<div></div>
		<div class="w-full h-auto">
			<div class="w-full my-3 pl-6" v-for="user in friendStore.friends">
				<div
					v-if="changedInitial(user.fullName ? user.fullName : '')"
					class="w-full h-8 mt-2 flex items-center"
				>
					<span
						class="w-fit mr-2 flex text-primary text-xs font-medium"
					>
						{{ user.fullName ? user.fullName[0] : "" }}
					</span>
					<span
						class="w-auto bg-color-background-mute flex flex-grow"
						style="height: 1px"
					></span>
				</div>
				<div class="w-full pr-6">
					<Friend
						:id="user.id as string"
						:display-name="user.userName as string"
						:img-url="user.profilePicUrl"
					/>
				</div>
			</div>
		</div>
	</div>
	<div
		class="modal-bg w-screen h-screen fixed flex items-center justify-center"
		v-if="request_prompt"
		@click="request_prompt = false"
	>
		<form
			class="modal-div max-w-full h-auto p-8 flex flex-col items-center"
			@click.stop
			@submit.prevent="createFriendRequest()"
		>
			<h4>ADD FRIEND</h4>
			<span class="mt-1 text-sm"
				>You can add friend with there usernames.</span
			>
			<input
				class="w-full h-10 mt-5 rounded-md"
				type="text"
				placeholder="username"
				v-model="username"
				required
			/>
			<input
				class="w-full h-10 mt-3 rounded-md"
				type="text"
				placeholder="message"
				v-model="message"
				required
			/>

			<button class="h-10 w-96 mt-6 rounded-md" type="submit">
				Send Friend Request
			</button>
		</form>
	</div>
</template>

<style scoped>
	.btn-bg {
		color: var(--primary);
		background: var(--color-background-mute);
		transition: 300ms;
	}

	.btn-bg:hover {
		color: var(--vt-c-white-soft);
		background: var(--primary);
	}

	.btn-ntf {
		color: var(--primary);
		background: transparent;
	}

	.modal-bg {
		top: 0;
		left: 0;
		background: rgba(0, 0, 0, 0.547);
		z-index: 100;
	}

	.modal-div {
		width: 800px;
		background: var(--color-background-mute);
	}

	h4 {
		color: var(--color-heading);
	}

	input {
		font-size: 17px;
		padding: 0.6rem;
		background: var(--color-background);
		border: none;
		outline: none;
	}

	input:focus {
		border: 1px solid var(--primary);
	}

	::placeholder {
		font-size: 16px;
		color: var(--color-text-soft);
		opacity: 1; /* Firefox */
	}

	::-ms-input-placeholder {
		/* Edge 12 -18 */
		color: var(--color-text-soft);
	}

	button {
		background: var(--primary);
		color: var(--vt-c-white-soft);
		transition: 200ms;
	}

	button:hover {
		color: var(--primary);
		background: var(--color-background);
	}
</style>
