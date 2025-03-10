<script setup lang="ts">
	import { ref } from "vue";
	import { Cropper } from "vue-advanced-cropper";
	import "vue-advanced-cropper/dist/style.css";
	import ZoomSlider from "./ZoomSlider.vue";
	import IconClose from "./icons/IconClose.vue";

	const props = defineProps<{ file: File | undefined }>();
	const zoom = ref(0);
	const cropper = ref<InstanceType<typeof Cropper> | null>(null);
	const img = URL.createObjectURL(props.file!);

	const emit = defineEmits<{
		(e: "modifiedFile", value: File): void;
		(e: "close"): void;
	}>();

	interface SizeRestrictions {
		minWidth: number;
		minHeight: number;
	}

	const defaultSize = ({
		imageSize,
	}: {
		imageSize: { width: number; height: number };
	}) => {
		return {
			width: Math.min(imageSize.height, imageSize.width),
			height: Math.min(imageSize.height, imageSize.width),
		};
	};

	const stencilSize = ({
		boundaries,
	}: {
		boundaries: { width: number; height: number };
	}) => {
		return {
			width: Math.min(boundaries.height, boundaries.width) - 48,
			height: Math.min(boundaries.height, boundaries.width) - 48,
		};
	};

	const onChange = () => {
		if (cropper.value) {
			const coordinates = cropper.value.coordinates as {
				width: number;
				height: number;
			};
			const imageSize = cropper.value.imageSize as {
				width: number;
				height: number;
			};
			const sizeRestrictions = cropper.value
				.sizeRestrictions as SizeRestrictions;
			if (
				imageSize.width / imageSize.height >
				coordinates.width / coordinates.height
			) {
				zoom.value =
					(imageSize.height - coordinates.height) /
					(imageSize.height - sizeRestrictions.minHeight);
			} else {
				zoom.value =
					(imageSize.width - coordinates.width) /
					(imageSize.width - sizeRestrictions.minWidth);
			}
		}
	};

	const onZoom = (value: number) => {
		if (cropper.value) {
			const imageSize = cropper.value.imageSize as {
				width: number;
				height: number;
			};
			const sizeRestrictions = cropper.value
				.sizeRestrictions as SizeRestrictions;

			if (imageSize.height < imageSize.width) {
				const minHeight = sizeRestrictions.minHeight;
				cropper.value.zoom(
					(imageSize.height -
						zoom.value * (imageSize.height - minHeight)) /
						(imageSize.height -
							value * (imageSize.height - minHeight))
				);
			} else {
				const minWidth = sizeRestrictions.minWidth;
				cropper.value.zoom(
					(imageSize.width -
						zoom.value * (imageSize.width - minWidth)) /
						(imageSize.width - value * (imageSize.width - minWidth))
				);
			}
		}
	};
	const getCropped = () => {
		console.log(cropper.value);
		if (cropper.value) {
			const result = cropper.value.getResult();
			if (result && result.canvas) {
				result.canvas.toBlob((blob) => {
					if (blob) {
						console.log(URL.createObjectURL(blob));
						const newFile = new File([blob], "fileName.jpg", {
							type: "image/jpeg",
						});

						emit("modifiedFile", newFile);
						emit("close");
					}
				}, "image/jpeg");
			}
		}
	};
</script>

<template>
	<div>
		<div
			class="w-[600px] h-[500px] bg-color-background absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-lg"
		>
			<div class="w-full h-full relative">
				<div
					class="w-full h-8 flex items-center justify-center relative bg-color-background-mute"
				>
					<span>Adjust the viewng portion</span>
					<button
						class="w-auto h-full aspect-square absolute right-0 top-0"
						@click="$emit('close')"
					>
						<IconClose />
					</button>
				</div>
				<div class="w-full h-[460px]">
					<Cropper
						ref="cropper"
						class="twitter-cropper"
						background-class="twitter-cropper__background"
						foreground-class="twitter-cropper__foreground"
						image-restriction="stencil"
						:stencil-size="stencilSize"
						:stencil-props="{
							lines: {},
							handlers: {},
							movable: false,
							scalable: false,
							aspectRatio: 1,
							previewClass: 'twitter-cropper__stencil',
						}"
						:transitions="false"
						:canvas="true"
						:debounce="false"
						:default-size="defaultSize"
						:min-width="150"
						:min-height="150"
						:src="img"
						@change="onChange"
					/>
				</div>
				<ZoomSlider :zoom="zoom" @change="onZoom" />

				<button
					class="w-16 h-auto aspect-square rounded-full flex items-center justify-center absolute bg-primary right-5 -bottom-5"
					@click="getCropped"
				>
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="currentColor"
						width="60%"
						height="60%"
					>
						<path
							d="M9.9997 15.1709L19.1921 5.97852L20.6063 7.39273L9.9997 17.9993L3.63574 11.6354L5.04996 10.2212L9.9997 15.1709Z"
						></path>
					</svg>
				</button>
			</div>
		</div>
	</div>
</template>

<style scoped>
	.twitter-cropper {
		height: 460px;
	}
	.twitter-cropper__background {
		background-color: #edf2f4;
	}
	.twitter-cropper__foreground {
		background-color: #edf2f4;
	}
	.twitter-cropper__stencil {
		border: solid 5px rgb(29, 161, 242);
	}
</style>
