import { defineStore } from "pinia";
import axios from "axios";
import { Socket } from "@/services/socektServices";
import { type Conversation } from "@/types/Conversation";
import { mapResponseToMessage, type Message } from "@/types/Message";
import { indexedDbService } from "@/services/indexDbServices";
import { useMessageStore } from "./message";
import { useUserStore } from "./user";

interface ConvResponse {
	id: string;
	participants: string[];
	unseen_message_ids: string[];
	start_date: string;
	last_message_date: string;
	messages: object[];
}

export const useSyncStore = defineStore("background_sync", () => {
	const userStore = useUserStore();

	const { isOnline, setOnline, setOffline } =
		userStore.useOnlineStatusManager();

	// Creating a new socket instance and connecting it to server
	const socket = new Socket("ws://localhost:8000/sync/socket");
	socket.connect();

	// Handle incoming WebSocket messages
	socket.on("message", async (msg) => {
		switch (msg.type) {
			case "online_status":
				// Update the user's online/offline status in local state
				if (msg.status == "online") setOnline(msg.user_id);
				else setOffline(msg.user_id);
				break;

			case "friend_update":
				console.log("friend_update");
				console.log(msg);
				break;
			case "friend_request":
				console.log("friend_request");
				console.log(msg);
				break;
		}
	});

	async function syncAndLoadConversationsFromLastDate() {
		const idbResponse = await indexedDbService.getAllRecords(
			"conversation"
		);

		let lastDate: string | null = null;

		if (idbResponse.objects.length > 0) {
			//arranging the conversatiton -> recent date first
			const conversations = (idbResponse.objects as Conversation[]).sort(
				(a, b) =>
					new Date(b.lastMessageDate as string).getTime() -
					new Date(a.lastMessageDate as string).getTime()
			);

			//adding each conversation to the gloval conversations variable
			await Promise.all(
				conversations.map(async (conv) => {
					userStore.conversations[conv.id as string] = {
						messages: [],
						participant: conv.participant as string,
						lastMessageDate: conv.lastMessageDate as string,
						isActive: true,
					};

					//retriving the messages for each conversation from IndesedDB and adding to glaobal varaible
					const messageRequest = await indexedDbService.getAllRecords(
						"message",
						{ conversationId: conv.id as string }
					);

					userStore.conversations[conv.id as string].messages = (
						messageRequest.objects as Message[]
					).sort(
						(a, b) =>
							new Date(a.sendingTime as string).getTime() -
							new Date(b.sendingTime as string).getTime()
					);
				})
			);

			console.log(userStore.conversations);

			lastDate = conversations[0].lastMessageDate;
		}

		//retriving the messages after latestMessage date
		const url = lastDate
			? `http://localhost:8000/conversation/list-conversations?after=${lastDate}`
			: "http://localhost:8000/conversation/list-conversations";

		const response = await axios({
			method: "get",
			url: url,
			withCredentials: true,
		});

		if (response.status === 200) {
			await Promise.all(
				(response.data as ConvResponse[]).map(async (conv) => {
					const messages: Message[] = conv.messages.map((msg) =>
						mapResponseToMessage(msg)
					);

					// Update the record to indexedDb
					const conversation: Conversation = {
						id: conv.id,
						unseenMessageIds: conv.unseen_message_ids,
						lastMessageDate: conv.last_message_date,
						participant: conv.participants.find(
							(id) => id != userStore.user.id
						) as string,
						startDate: conv.start_date,
					};

					await indexedDbService.updateRecord(
						"conversation",
						conversation
					);

					//add each message to indexedDb
					await indexedDbService.batchInsert("message", messages);

					// Initialize conversation if not exists
					userStore.conversations[conv.id] ??= {
						messages: [],
						participant: conv.participants.find(
							(id) => id != userStore.user.id
						) as string,
						lastMessageDate: "",
						isActive: true,
					};

					// Update the message and date
					userStore.conversations[conv.id].messages = messages;
					userStore.conversations[conv.id].lastMessageDate =
						conv.last_message_date;
				})
			);
		}
	}

	return { syncAndLoadConversationsFromLastDate };
});
