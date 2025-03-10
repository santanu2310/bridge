<script setup lang="ts">
	import { ref, onMounted, onUnmounted, defineProps } from "vue";

	type DragEvent = MouseEvent | TouchEvent;
	const emit = defineEmits<{ (e: "change", value: number): void }>();

	const props = defineProps<{ zoom: number }>();
	const focus = ref(false);
	const line = ref<HTMLDivElement | null>(null);

	const onDrag = (e: DragEvent) => {
		if (!focus.value || !line.value) return;
		const position = "touches" in e ? e.touches[0].clientX : e.clientX;
		const { left, width } = line.value.getBoundingClientRect();
		emit("change", Math.min(1, Math.max(0, (position - left) / width)));
		e.preventDefault?.();
	};

	const onStop = () => {
		focus.value = false;
	};

	const onStart = (e: DragEvent) => {
		focus.value = true;
		onDrag(e);
	};

	onMounted(() => {
		window.addEventListener("mouseup", onStop, { passive: false });
		window.addEventListener("mousemove", onDrag, { passive: false });
		window.addEventListener("touchmove", onDrag, { passive: false });
		window.addEventListener("touchend", onStop, { passive: false });
	});

	onUnmounted(() => {
		window.removeEventListener("mouseup", onStop);
		window.removeEventListener("mousemove", onDrag);
		window.removeEventListener("touchmove", onDrag);
		window.removeEventListener("touchend", onStop);
	});
</script>

<template>
	<div class="twitter-navigation">
		<div class="twitter-navigation__wrapper">
			<div
				class="twitter-navigation__zoom-icon twitter-navigation__zoom-icon--left"
			>
				<svg viewBox="0 0 24 24" class="icon-svg">
					<g>
						<path
							d="M21.53 20.47l-3.66-3.66C19.195 15.24 20 13.214 20 11c0-4.97-4.03-9-9-9s-9 4.03-9 9 4.03 9 9 9c2.215 0 4.24-.804 5.808-2.13l3.66 3.66c.147.146.34.22.53.22s.385-.073.53-.22c.295-.293.295-.767.002-1.06zM3.5 11c0-4.135 3.365-7.5 7.5-7.5s7.5 3.365 7.5 7.5-3.365 7.5-7.5 7.5-7.5-3.365-7.5-7.5z"
						></path>
						<path
							d="M14.46 11.75H7.54c-.414 0-.75-.336-.75-.75s.336-.75.75-.75h6.92c.415 0 .75.336.75.75s-.335.75-.75.75z"
						></path>
					</g>
				</svg>
			</div>
			<div
				class="twitter-navigation__line-wrapper"
				ref="line"
				@mousedown="onStart"
				@touchstart="onStart"
			>
				<div class="twitter-navigation__line">
					<div
						class="twitter-navigation__fill"
						:style="{ flexGrow: props.zoom }"
					></div>
					<div
						class="twitter-navigation__circle"
						:class="{ 'twitter-navigation__circle--focus': focus }"
						:style="{ left: `${props.zoom * 100}%` }"
					>
						<div
							class="twitter-navigation__inner-circle"
							:class="{
								'twitter-navigation__inner-circle--focus':
									focus,
							}"
						></div>
					</div>
				</div>
			</div>
			<div
				class="twitter-navigation__zoom-icon twitter-navigation__zoom-icon--right"
			>
				<svg viewBox="0 0 24 24" class="icon-svg">
					<g>
						<path
							d="M21.53 20.47l-3.66-3.66C19.195 15.24 20 13.214 20 11c0-4.97-4.03-9-9-9s-9 4.03-9 9 4.03 9 9 9c2.215 0 4.24-.804 5.808-2.13l3.66 3.66c.147.146.34.22.53.22s.385-.073.53-.22c.295-.293.295-.767.002-1.06zM3.5 11c0-4.135 3.365-7.5 7.5-7.5s7.5 3.365 7.5 7.5-3.365 7.5-7.5 7.5-7.5-3.365-7.5-7.5z"
						></path>
						<path
							d="M15.21 11c0 .41-.34.75-.75.75h-2.71v2.71c0 .41-.34.75-.75.75s-.75-.34-.75-.75v-2.71H7.54c-.41 0-.75-.34-.75-.75s.34-.75.75-.75h2.71V7.54c0-.41.34-.75.75-.75s.75.34.75.75v2.71h2.71c.41 0 .75.34.75.75z"
						></path>
					</g>
				</svg>
			</div>
		</div>
	</div>
</template>

<style scoped>
	.twitter-navigation {
		display: flex;
		width: 100%;
		align-items: center;
		justify-content: center;
		height: 50px;
	}
	.twitter-navigation__wrapper {
		display: flex;
		align-items: center;
		max-width: 400px;
		width: 100%;
	}
	.icon-svg {
		height: 18.75px;
		width: 18.75px;
		fill: rgb(101, 119, 134);
	}
	.twitter-navigation__line-wrapper {
		width: 100%;
		height: 20px;
		display: flex;
		margin: 0 10px;
		align-items: center;
		border-radius: 5px;
		cursor: pointer;
	}
	.twitter-navigation__line {
		background: rgb(142, 208, 249);
		height: 5px;
		width: 100%;
		border-radius: 5px;
		position: relative;
	}
	.twitter-navigation__fill {
		background: rgb(29, 161, 242);
	}
	.twitter-navigation__circle {
		width: 30px;
		height: 30px;
		border-radius: 50%;
		position: absolute;
		display: flex;
		align-items: center;
		justify-content: center;
		top: -12.5px;
		transform: translateX(-50%);
	}
	.twitter-navigation__inner-circle {
		width: 15px;
		height: 15px;
		border-radius: 50%;
		background-color: rgb(29, 161, 242);
	}
</style>
