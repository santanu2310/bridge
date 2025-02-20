<script setup lang="ts">
	interface Props {
		size?: number;
	}
	const { size = 60 } = defineProps<Props>();
</script>

<template>
	<svg
		xmlns="http://www.w3.org/2000/svg"
		viewBox="0 0 24 24"
		fill="currentColor"
		:width="`${size}%`"
		:height="`${size}%`"
	>
		<path
			d="M10.8284 12.0007L15.7782 16.9504L14.364 18.3646L8 12.0007L14.364 5.63672L15.7782 7.05093L10.8284 12.0007Z"
		></path>
	</svg>
</template>
