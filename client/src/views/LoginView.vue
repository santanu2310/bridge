<script setup lang="ts">
	import { ref } from "vue";
	import { RouterLink, useRouter } from "vue-router";
	import axios from "axios";

	import { useAuthStore } from "@/stores/auth";
	import { indexedDbService } from "@/services/indexDbServices";

	const router = useRouter();
	const authStore = useAuthStore();
	const passwordVisible = ref(false);

	const username = ref("");
	const password = ref("");

	async function getToken() {
		try {
			const response = await axios({
				method: "post",
				url: "http://localhost:8000/user/get-token",
				data: `username=${username.value}&password=${password.value}`,
				withCredentials: true,
			});

			console.log(response.status);

			if (response.status === 200) {
				authStore.isAuthenticated = true;
				indexedDbService.clearDatabase();
				router.push({ name: "home" });
			}
		} catch (error) {
			console.log(error);
		}
	}
</script>

<template>
	<div
		class="login w-full flex lg:flex-row flex-col items-center lg:items-start"
	>
		<div
			class="xl:w-1/4 lg:w-2/6 lg:h-screen flex flex-col items-center relative top-0"
		>
			<div class="w-60 mt-10 flex flex-col">
				<div
					class="logo w-full h-12 flex justify-center lg:justify-start"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="currentColor"
						height="42px"
						width="auto"
						class="mr-1"
					>
						<path
							d="M2 8.99374C2 5.68349 4.67654 3 8.00066 3H15.9993C19.3134 3 22 5.69478 22 8.99374V21H8.00066C4.68659 21 2 18.3052 2 15.0063V8.99374ZM14 11V13H16V11H14ZM8 11V13H10V11H8Z"
						></path>
					</svg>
					<span class="text-4xl font-bold">Bridge</span>
				</div>
				<div class="text-sm text-center lg:text-start">
					The shotrest bridge for connection
				</div>
			</div>
			<div class="mt-auto lg:block hidden">
				<img
					class="auth-img relative"
					src="@/assets/auth-img.png"
					alt=""
				/>
			</div>
		</div>
		<div
			class="login-f-wrapper xl:w-3/4 lg:w-4/6 w-11/12 h-auto lg:mr-10 my-10 py-6 sm:px-10 px-2 flex flex-col items-center justify-center rounded-2xl"
		>
			<div
				class="login-form max-w-80 w-full mb-20 flex flex-col items-center"
			>
				<div class="my-12 text-center">
					<b class="text-3xl font-medium">Welcome Back</b>
					<p class="mt-1 text-base">Sign in to continue to Bridge.</p>
				</div>
				<form class="w-full" @submit.prevent="getToken()">
					<div class="input-div">
						<label class="text-base font-medium" for="username"
							>Username</label
						>
						<input
							type="text"
							id="username"
							v-model="username"
							placeholder="Enter Username"
							required
						/>
					</div>
					<div class="input-div">
						<label class="text-base font-medium" for="password"
							>Password</label
						>
						<div class="h-10 mt-2.5 flex">
							<input
								:type="passwordVisible ? 'text' : 'password'"
								id="password"
								v-model="password"
								placeholder="Enter Password"
								required
							/>
							<span
								class="eye w-10 h-10 flex items-center justify-center"
								@click="
									passwordVisible = passwordVisible
										? false
										: true
								"
							>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 24 24"
									fill="currentColor"
									:class="[
										{ hidden: passwordVisible },
										'w-2/5',
									]"
								>
									<path
										d="M1.18164 12C2.12215 6.87976 6.60812 3 12.0003 3C17.3924 3 21.8784 6.87976 22.8189 12C21.8784 17.1202 17.3924 21 12.0003 21C6.60812 21 2.12215 17.1202 1.18164 12ZM12.0003 17C14.7617 17 17.0003 14.7614 17.0003 12C17.0003 9.23858 14.7617 7 12.0003 7C9.23884 7 7.00026 9.23858 7.00026 12C7.00026 14.7614 9.23884 17 12.0003 17ZM12.0003 15C10.3434 15 9.00026 13.6569 9.00026 12C9.00026 10.3431 10.3434 9 12.0003 9C13.6571 9 15.0003 10.3431 15.0003 12C15.0003 13.6569 13.6571 15 12.0003 15Z"
									></path>
								</svg>
								<svg
									xmlns="http://www.w3.org/2000/svg"
									viewBox="0 0 24 24"
									fill="currentColor"
									:class="[
										{ hidden: !passwordVisible },
										'w-2/5',
									]"
								>
									<path
										d="M10.1305 15.8421L9.34268 18.7821L7.41083 18.2645L8.1983 15.3256C7.00919 14.8876 5.91661 14.2501 4.96116 13.4536L2.80783 15.6069L1.39362 14.1927L3.54695 12.0394C2.35581 10.6105 1.52014 8.8749 1.17578 6.96843L2.07634 6.80469C4.86882 8.81573 8.29618 10.0003 12.0002 10.0003C15.7043 10.0003 19.1316 8.81573 21.9241 6.80469L22.8247 6.96843C22.4803 8.8749 21.6446 10.6105 20.4535 12.0394L22.6068 14.1927L21.1926 15.6069L19.0393 13.4536C18.0838 14.2501 16.9912 14.8876 15.8021 15.3256L16.5896 18.2645L14.6578 18.7821L13.87 15.8421C13.2623 15.9461 12.6376 16.0003 12.0002 16.0003C11.3629 16.0003 10.7381 15.9461 10.1305 15.8421Z"
									></path>
								</svg>
							</span>
						</div>
					</div>

					<span class="w-full my-5 block text-sm"
						>By registering you agree to the Bridge Terms of
						Use</span
					>
					<button
						type="submit"
						class="button w-full h-10 rounded-lg font-medium"
					>
						Login
					</button>
				</form>
				<span class="mt-6"
					>Don't have an account ?
					<RouterLink to="register" class="link"
						>Register</RouterLink
					></span
				>
			</div>
			<div class="text-center">
				<span class="text-sm md:text-base">
					© 2024 Bridge. Crafted with <b class="text-white">❤️</b> by
					Santanu
				</span>
			</div>
		</div>
	</div>
</template>

<style scoped>
	.login {
		background: var(--primary);
	}

	.login-f-wrapper {
		background-color: var(--color-background-mute);
	}

	.login-form > div > b {
		color: var(--color-heading);
	}

	.input-div {
		width: 100%;
		height: auto;
		margin-bottom: 20px;
		display: flex;
		flex-direction: column;
	}

	.input-div > label {
		color: var(--color-heading);
	}

	input {
		width: 100%;
		margin-top: 10px;
		padding: 0.5rem 1rem;
		border-radius: 8px;
		font-size: 0.875rem;
		line-height: 1.5rem;
		font-weight: 400;
		border: none;
		outline: none;
		background: var(--color-background);
		color: var(--color-text);
	}

	#password {
		width: calc(100% - 45px);
		margin-top: 0;
		border-top-right-radius: 0;
		border-bottom-right-radius: 0;
	}

	.eye {
		background: var(--color-background);
	}

	.button {
		background: var(--primary);
		color: var(--color-background);
	}

	.link {
		color: var(--primary);
	}

	.logo {
		color: var(--color-text);
	}

	.auth-img {
		max-width: 160%;
	}

	@media (max-width: 1280px) {
		.auth-img {
			max-width: 140%;
		}
	}
</style>
