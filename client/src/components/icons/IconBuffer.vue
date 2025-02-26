<script setup lang="ts">
	interface Props {
		size?: number;
	}
	const { size = 60 } = defineProps<Props>();
</script>

<template>
	<div class="w-8 h-8 inline-block overflow-hidden">
		<div class="ldio-x2uulkbinc">
			<div></div>
		</div>
	</div>
</template>
<style lang="css" scoped>
	@keyframes ldio-x2uulkbinc {
		0% {
			transform: translate(-50%, -50%) rotate(0deg);
		}
		100% {
			transform: translate(-50%, -50%) rotate(360deg);
		}
	}
	.ldio-x2uulkbinc div {
		position: absolute;
		width: 70%;
		height: 70%;
		border: 4.4px solid #1382c2;
		border-top-color: transparent;
		border-radius: 50%;
	}
	.ldio-x2uulkbinc div {
		animation: ldio-x2uulkbinc 1s linear infinite;
		/* top: 85px;
		left: 85px; */
		top: 50%;
		left: 50%;
	}

	.ldio-x2uulkbinc {
		width: 100%;
		height: 100%;
		position: relative;
		transform: translateZ(0) scale(1);
		backface-visibility: hidden;
		transform-origin: 0 0;
	}
	.ldio-x2uulkbinc div {
		box-sizing: content-box;
	}
</style>
