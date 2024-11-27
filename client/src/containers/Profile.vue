<script setup lang="ts">
	import IconSettings from "@/components/icons/IconSettings.vue";
</script>

<template>
	<div class="w-full h-full p-8">
		<div class="w-full h-8 flex items-center justify-between">
			<span class="font-medium text-xl">Profile</span>
			<button
				class="w-auto h-full aspect-square outline-none border-none flex items-center justify-between"
				@click="$emit('switchContainer', 'settings')"
			>
				<IconSettings />
			</button>
		</div>
		<div
			class="w-full h-auto aspect-square flex justify-center items-center"
		>
			<div
				class="w-3/5 h-auto aspect-square rounded-full overflow-hidden"
			>
				<img
					src="https://doot-dark.react.themesbrand.com/static/media/avatar-1.9c8e605558cece65b06c.jpg"
					alt=""
				/>
			</div>
		</div>
		<div class=""></div>
	</div>
</template>

<style></style>
