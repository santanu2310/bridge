/** @type {import('tailwindcss').Config} */
export default {
	purge: ["./index.html", "./src/**/*.{vue,js,ts,jsx,tsx}"],
	content: [],
	darkMode: true,
	theme: {
		extend: {
			margin: {
				"n-50": "-20%",
			},
			colors: {
				"color-background": "#232427",
				"color-background-soft": "#2b2d31",
				"color-background-mute": "#313338",
				primary: "#1382c2",
				"color-text": "#3c3c3ca8",
				"color-heading": "#c2cbd4",
				"green-500": "#10b783",
				"color-white": "#fff",
			},
		},
	},
	plugins: [],
};
