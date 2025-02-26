<script setup lang="ts">
	import { computed, defineProps } from "vue";

	interface Props {
		progress: number;
	}

	const props = defineProps<Props>();

	const radius = 15;
	const circumference = 2 * Math.PI * radius;

	const dashOffset = computed(() => {
		return circumference - (props.progress / 100) * circumference;
	});

	const progressStyle = computed(() => ({
		strokeDasharray: `${circumference}`,
		strokeDashoffset: `${dashOffset.value}`,
	}));
</script>
<template>
	<div class="progress-container w-11 h-11 relative">
		<svg width="44" height="44">
			<!-- Background circle -->
			<circle
				class="stroke-color-background-mute"
				cx="22"
				cy="22"
				:r="radius"
			></circle>
			<!-- Progress circle -->
			<circle
				class="progress-bar stroke-primary"
				cx="22"
				cy="22"
				:r="radius"
				:style="progressStyle"
			></circle>
		</svg>
		<div
			class="progress-text w-fit h-fit absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-color-heading text-xxs"
			id="progressText"
		>
			{{ progress }}%
		</div>
	</div>
</template>

<style scoped>
	/* Rotate SVG to start progress from the top */
	.progress-container svg {
		transform: rotate(-90deg);
	}
	.progress-container circle {
		fill: none;
		stroke-width: 4;
		stroke-linecap: round;
	}

	.progress-bar {
		stroke-dasharray: 440;
		stroke-dashoffset: 440;
		transition: stroke-dashoffset 0.5s ease;
	}
</style>
