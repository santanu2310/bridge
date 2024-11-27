import { defineStore } from "pinia";

export const useSyncStore = defineStore("background_sync", () => {
	const socket = new WebSocket("ws://localhost:8000/sync/socket");
});
