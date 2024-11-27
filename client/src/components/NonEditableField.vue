<script setup lang="ts">
	const props = defineProps<{
		d_value: string;
		label: string;
	}>();
</script>

<template>
	<div class="w-full h-auto">
		<span class="text-sm font-light leading-4">{{ props.label }}</span>
		<span
			class="w-full h-8 mt-1 block text-color-heading text-sm font-medium"
			>{{ props.d_value }}</span
		>
	</div>
</template>
