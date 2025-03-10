<script setup lang="ts">
	import { ref } from "vue";
	import IconPencil from "@/components/icons/IconPencil.vue";
	import EditableField from "@/components/EditableField.vue";
	import NonEditableField from "@/components/NonEditableField.vue";
	import EditProfilePicture from "@/components/EditProfilePicture.vue";

	import { useUserStore } from "@/stores/user";
	import { useAuthStore } from "@/stores/auth";
	import IconCamera from "@/components/icons/IconCamera.vue";

	const userStore = useUserStore();
	const authStore = useAuthStore();

	const user = ref(userStore.user);

	const profileInputReference = ref<HTMLInputElement | null>(null);
	const editProfilePopup = ref(false);

	const isVisible = ref<string | null>("p_info");
	function changeVisibility(v_value: string) {
		isVisible.value = isVisible.value != v_value ? v_value : null;
	}

	const uploadProfilePic = async (file: File) => {
		// const file = profileInputReference.value?.files![0];
		if (file) {
			if (file.size > 10 * 1024 * 1024) {
				alert("File size exceeds 10MB. Please select a smaller file.");
				profileInputReference.value = null;
			} else {
				// Get the upload url and other metadata
				const response = await authStore.authAxios({
					method: "get",
					url: "users/upload-url",
				});
				console.log(response);

				if (response.status === 200) {
					console.log(file);
					response.data.fields["file"] = file;

					// Upload the file to aws
					const uploadResponse = await authStore.publicAxios({
						method: "post",
						headers: {
							"Content-Type": "multipart/form-data",
						},
						url: response.data.url,
						data: response.data.fields,
					});

					console.log("status code : ", uploadResponse.status);

					if (uploadResponse.status === 204) {
						const profile_data = {
							profile_picture_id: response.data.fields.key,
						};

						const messageResponse = await authStore.authAxios({
							method: "post",
							url: "users/add-profile-image",
							data: profile_data,
						});

						console.log(messageResponse);
					}
				}
			}
		}
	};

	const onClose = () => {
		profileInputReference.value = null;
		editProfilePopup.value = false;
	};
</script>

<template>
	<div class="max-h-svh overflow-auto">
		<div class="w-full flex flex-col items-center">
			<div class="w-full h-40 mb-20 relative bg-slate-900">
				<img
					src="https://res.cloudinary.com/omaha-code/image/upload/ar_4:3,c_fill,dpr_1.0,e_art:quartz,g_auto,h_396,q_auto:best,t_Linkedin_official,w_1584/v1561576558/mountains-1412683_1280.png"
					alt=""
					class="w-full h-full object-cover opacity-50"
				/>
				<div
					class="w-full h-8 my-6 px-6 absolute top-0 flex items-center justify-between"
				>
					<span class="text-xl font-semibold text-color-white"
						>Settings</span
					>
					<button
						class="h-full aspect-square flex items-center justify-center rounded-full"
					>
						<IconPencil />
					</button>
				</div>
				<div
					class="w-2/5 aspect-auto absolute left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full overflow-hidden"
				>
					<div class="w-full h-full relative">
						<label
							for="profilepic"
							class="w-full h-full flex flex-col items-center justify-center absolute top-0 left-0 bg-slate-900 bg-opacity-70 text-sm text-center delay-300 hover:z-10"
						>
							<div class="w-1/6 h-auto aspect-square">
								<IconCamera :size="90" />
							</div>
							UPLOAD PROFILE PICTURE
						</label>
						<input
							type="file"
							name="profilepic"
							id="profilepic"
							hidden
							ref="profileInputReference"
							max="20971520"
							accept="image/*"
							@change="editProfilePopup = true"
						/>
						<img
							class="w-full h-full object-cover relative delay-300 hover:-z-10"
							src="https://doot-dark.react.themesbrand.com/static/media/avatar-1.9c8e605558cece65b06c.jpg"
							alt=""
						/>
					</div>
					<Teleport to="body">
						<EditProfilePicture
							v-if="editProfilePopup"
							:file="profileInputReference?.files![0]"
							@close="onClose"
							@modifiedFile="uploadProfilePic"
						/>
					</Teleport>
				</div>
			</div>
			<div class="w-full mt-2 mb-10 flex flex-col items-center">
				<span class="mb-1 text-base font-medium">Santanu Majumder</span>
				<span class="flex items-center text-xs font-medium"
					><small
						class="w-2 h-2 mr-1 block bg-green-500 rounded-full"
					></small
					>Active</span
				>
			</div>
			<div class="w-full">
				<div class="border-y border-y-color-background-mute">
					<div
						class="w-full h-10 p-6 flex items-center justify-between"
						:class="{
							'bg-color-background-mute': isVisible == 'p_info',
						}"
						@click="changeVisibility('p_info')"
					>
						<span class="w-auto flex"
							><svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								width="1rem"
								height="1rem"
							>
								<path
									d="M11.9999 17C15.6623 17 18.8649 18.5751 20.607 20.9247L18.765 21.796C17.3473 20.1157 14.8473 19 11.9999 19C9.15248 19 6.65252 20.1157 5.23479 21.796L3.39355 20.9238C5.13576 18.5747 8.33796 17 11.9999 17ZM11.9999 2C14.7613 2 16.9999 4.23858 16.9999 7V10C16.9999 12.7614 14.7613 15 11.9999 15C9.23847 15 6.9999 12.7614 6.9999 10V7C6.9999 4.23858 9.23847 2 11.9999 2Z"
								></path>
							</svg>
							<p class="ml-2 text-xs font-semibold">
								Personal Info
							</p></span
						>
						<span
							class="duration-200"
							:class="{ 'rotate-180': isVisible == 'p_info' }"
							><svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								width="1rem"
								height="1rem"
							>
								<path
									d="M11.9999 13.1714L16.9497 8.22168L18.3639 9.63589L11.9999 15.9999L5.63599 9.63589L7.0502 8.22168L11.9999 13.1714Z"
								></path></svg
						></span>
					</div>
					<div
						class="w-full h-0 px-8 overflow-hidden duration-200 max-h-screen"
						:class="{
							['!h-[280px]']: isVisible == 'p_info',
						}"
					>
						<div class="w-full mt-2">
							<EditableField
								d_key="full_name"
								:d_value="user.fullName || ''"
								label="Display Name"
							/>
						</div>

						<div class="w-full mt-2">
							<NonEditableField
								:d_value="user.email as string"
								label="User Email"
							/>
						</div>
						<div class="w-full mt-2">
							<EditableField
								d_key="bio"
								:d_value="user.bio || ''"
								label="Bio"
							/>
						</div>
						<div class="w-full mt-2">
							<EditableField
								d_key="location"
								:d_value="user.location || ''"
								label="Location"
							/>
						</div>
					</div>
				</div>
				<div class="border-y border-y-color-background-mute">
					<div
						class="w-full h-10 p-6 flex items-center justify-between"
						:class="{
							'bg-color-background-mute': isVisible == 'themes',
						}"
						@click="changeVisibility('themes')"
					>
						<span class="w-auto flex"
							><svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								width="1rem"
								height="1rem"
							>
								<path
									d="M12 21.9967C6.47715 21.9967 2 17.5196 2 11.9967C2 6.47386 6.47715 1.9967 12 1.9967C17.5228 1.9967 22 6.47386 22 11.9967C22 17.5196 17.5228 21.9967 12 21.9967ZM12 19.9967C16.4183 19.9967 20 16.415 20 11.9967C20 7.57843 16.4183 3.9967 12 3.9967C7.58172 3.9967 4 7.57843 4 11.9967C4 16.415 7.58172 19.9967 12 19.9967ZM7.00035 15.316C9.07995 15.1646 11.117 14.2939 12.7071 12.7038C14.2972 11.1137 15.1679 9.07666 15.3193 6.99706C15.6454 7.21408 15.955 7.46642 16.2426 7.75406C18.5858 10.0972 18.5858 13.8962 16.2426 16.2393C13.8995 18.5825 10.1005 18.5825 7.75736 16.2393C7.46971 15.9517 7.21738 15.6421 7.00035 15.316Z"
								></path>
							</svg>
							<p class="ml-2 text-xs font-semibold">Themes</p>
						</span>
						<span
							class="duration-200"
							:class="{ 'rotate-180': isVisible == 'themes' }"
							><svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								width="1rem"
								height="1rem"
							>
								<path
									d="M11.9999 13.1714L16.9497 8.22168L18.3639 9.63589L11.9999 15.9999L5.63599 9.63589L7.0502 8.22168L11.9999 13.1714Z"
								></path></svg
						></span>
					</div>
				</div>
				<div class="border-y border-y-color-background-mute">
					<div
						class="w-full h-10 p-6 flex items-center justify-between"
						:class="{
							'bg-color-background-mute': isVisible == 'privacy',
						}"
						@click="changeVisibility('privacy')"
					>
						<span class="w-auto flex"
							><svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								width="1rem"
								height="1rem"
							>
								<path
									d="M12 1C8.68629 1 6 3.68629 6 7V8H4C3.44772 8 3 8.44772 3 9V21C3 21.5523 3.44772 22 4 22H13.044C12.6947 21.2389 12.5 20.3922 12.5 19.5C12.5 16.1863 15.1863 13.5 18.5 13.5C19.3922 13.5 20.2389 13.6947 21 14.044V9C21 8.44772 20.5523 8 20 8H18V7C18 3.68629 15.3137 1 12 1ZM16 8H8V7C8 4.79086 9.79086 3 12 3C14.2091 3 16 4.79086 16 7V8ZM21.145 23.1406L20.6399 20.1953L22.7798 18.1094L19.8225 17.6797L18.5 15L17.1775 17.6797L14.2202 18.1094L16.3601 20.1953L15.855 23.1406L18.5 21.75L21.145 23.1406Z"
								></path>
							</svg>
							<p class="ml-2 text-xs font-semibold">
								Privacy
							</p></span
						>
						<span
							class="duration-200"
							:class="{ 'rotate-180': isVisible == 'privacy' }"
							><svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								width="1rem"
								height="1rem"
							>
								<path
									d="M11.9999 13.1714L16.9497 8.22168L18.3639 9.63589L11.9999 15.9999L5.63599 9.63589L7.0502 8.22168L11.9999 13.1714Z"
								></path></svg
						></span>
					</div>
				</div>
				<div class="border-y border-y-color-background-mute">
					<div
						class="w-full h-10 p-6 flex items-center justify-between"
						:class="{
							'bg-color-background-mute': isVisible == 'help',
						}"
						@click="changeVisibility('help')"
					>
						<span class="w-auto flex"
							><svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								width="1rem"
								height="1rem"
							>
								<path
									d="M12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22ZM11 15V17H13V15H11ZM13 13.3551C14.4457 12.9248 15.5 11.5855 15.5 10C15.5 8.067 13.933 6.5 12 6.5C10.302 6.5 8.88637 7.70919 8.56731 9.31346L10.5288 9.70577C10.6656 9.01823 11.2723 8.5 12 8.5C12.8284 8.5 13.5 9.17157 13.5 10C13.5 10.8284 12.8284 11.5 12 11.5C11.4477 11.5 11 11.9477 11 12.5V14H13V13.3551Z"
								></path>
							</svg>
							<p class="ml-2 text-xs font-semibold">Help</p></span
						>
						<span
							class="duration-200"
							:class="{ 'rotate-180': isVisible == 'help' }"
							><svg
								xmlns="http://www.w3.org/2000/svg"
								viewBox="0 0 24 24"
								fill="currentColor"
								width="1rem"
								height="1rem"
							>
								<path
									d="M11.9999 13.1714L16.9497 8.22168L18.3639 9.63589L11.9999 15.9999L5.63599 9.63589L7.0502 8.22168L11.9999 13.1714Z"
								></path></svg
						></span>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>
