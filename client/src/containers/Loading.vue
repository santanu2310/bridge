<template>
	<div class="body w-screen h-screen flex items-center justify-center">
		<div class="w-fit h-auto flex items-center flex-col">
			<div class="logo">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 24 24"
					height="48"
					width="48"
					class="mr-1"
					fill="currentColor"
				>
					<path
						d="M2 8.99374C2 5.68349 4.67654 3 8.00066 3H15.9993C19.3134 3 22 5.69478 22 8.99374V21H8.00066C4.68659 21 2 18.3052 2 15.0063V8.99374ZM14 11V13H16V11H14ZM8 11V13H10V11H8Z"
					></path>
				</svg>
			</div>
			<span class="btn-shine"> Get ready to be connected </span>
		</div>
	</div>
</template>
<style scoped>
	body {
		background: #000;
		font-family: "Poppins", sans-serif;
		-webkit-font-smoothing: antialiased;
		-moz-osx-font-smoothing: grayscale;
	}
	.logo {
		color: #fff;
	}
	.btn-shine {
		padding: 12px 48px;
		color: #fff;
		background: linear-gradient(to right, #7c7c7c 0, #fff 10%, #7c7c7c 20%);
		background-position: 0;
		background-clip: border-box;
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		animation: shine 2s infinite linear;
		animation-fill-mode: forwards;
		-webkit-text-size-adjust: none;
		font-weight: 600;
		font-size: 16px;
		text-decoration: none;
		white-space: nowrap;
	}

	.logo svg {
		mask-image: linear-gradient(
			-90deg,
			rgba(0, 0, 0, 0.7) 30%,
			#000000 50%,
			rgba(0, 0, 0, 0.7) 70%
		);
		mask-size: 200%;
		animation: shineing 2s infinite;
	}

	@keyframes shineing {
		from {
			-webkit-mask-position: 150%;
		}
		to {
			-webkit-mask-position: -50%;
		}
	}

	@-moz-keyframes shine {
		0% {
			background-position: 0;
		}
		60% {
			background-position: 160px;
		}
		100% {
			background-position: 280px;
		}
	}
	@-webkit-keyframes shine {
		0% {
			background-position: 0;
		}
		60% {
			background-position: 160px;
		}
		100% {
			background-position: 280px;
		}
	}
	@-o-keyframes shine {
		0% {
			background-position: 0;
		}
		60% {
			background-position: 160px;
		}
		100% {
			background-position: 280px;
		}
	}
	@keyframes shine {
		0% {
			background-position: 0;
		}
		60% {
			background-position: 160px;
		}
		100% {
			background-position: 280px;
		}
	}
</style>
