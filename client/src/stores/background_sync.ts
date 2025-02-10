import { defineStore } from "pinia";
import axios from "axios";
import { Socket } from "@/services/socektServices";
import { type Conversation } from "@/types/Conversation";
import { mapResponseToMessage, type Message } from "@/types/Message";
import {
	MessageStatus,
	SyncMessageType,
	type MessageEvent,
	type MessageStatusUpdate,
} from "@/types/SocketEvents";
import { indexedDbService } from "@/services/indexDbServices";
import { useUserStore } from "./user";
import { updateMessageInState } from "@/utils/MessageUtils";

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

			case "message_status":
				// Iterate over the data which contain message_id and timestamp
				for (const obj of msg.data) {
					// Retrive the message from indexedDb
					const message = (await indexedDbService.getRecord(
						"message",
						obj.message_id
					)) as Message;

					if (!message) continue; // Ensure message exists before proceeding

					// Modify the message status and timestamp
					message.status = msg.status;
					if (msg.status == MessageStatus.received)
						message.receivedTime = obj.timestamp;
					else {
						message.seenTime = obj.timestamp;
					}

					// Update the indexdDb record
					await indexedDbService.updateRecord("message", message);

					// Update the state(store ref variable)
					updateMessageInState(message);
				}
				break;

			case "friend_request":
				console.log("friend_request");
				console.log(msg);
				break;
		}
	});

	async function sendMessage(data: MessageStatusUpdate) {
		socket.send(data);
	}

	async function markMessageAsSeen(message: Message) {
		// Prevent unnecessary updates if the message is already marked as "seen"
		if (message.status === MessageStatus.seen) return;

		console.log(
			"Sending seen status to server for messageId : ",
			message.id
		);

		// Generate a timestamp for when the message is seen
		const seenDateTime = new Date().toISOString();

		// Prepare a status update payload for newly received messages
		const data: MessageEvent = {
			message_id: message.id as string,
			timestamp: seenDateTime,
		};
		const statusUpdate: MessageStatusUpdate = {
			type: SyncMessageType.MessageStatus,
			data: [data],
			status: MessageStatus.seen,
		};
		try {
			// Send updated status to the server
			await sendMessage(statusUpdate);

			// Update the message data
			message.status = MessageStatus.seen;
			message.seenTime = seenDateTime;

			// Update indesedDB record
			await indexedDbService.updateRecord("message", message);

			// Update UI state
			updateMessageInState(message);
		} catch (error) {
			console.error("Failed processaing seen status : ", error);
		}
	}

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
					// Prepare a status update payload for newly received messages
					const statusUpdate: MessageStatusUpdate = {
						type: SyncMessageType.MessageStatus,
						data: [],
						status: MessageStatus.received,
					};

					// Map response messages to `Message` objects and update their status if needed
					const messages: Message[] = conv.messages.map((msg) => {
						// Map the message response to Message object
						const message = mapResponseToMessage(msg);
						const receivedTime = new Date().toISOString();

						// Update the newly received message status and timestamp and add it to `statusUpdate`
						if (message.status == MessageStatus.send) {
							const data: MessageEvent = {
								message_id: message.id as string,
								timestamp: receivedTime,
							};

							statusUpdate.data.push(data);

							message.status = MessageStatus.received;
							message.receivedTime = receivedTime;
						}
						return message;
					});

					console.log("messages : ", messages);

					// Update the record to indexedDb
					const conversation: Conversation = {
						id: conv.id,
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
					await indexedDbService.batchUpsert("message", messages);

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

					await sendMessage(statusUpdate);
				})
			);
		}
	}

	async function syncMessageStatus() {
		// Fetch all conversation record from indesedDB
		const idbResponse = await indexedDbService.getAllRecords(
			"conversation"
		);

		if (idbResponse.objects.length > 0) {
			//arranging the conversatiton -> recent date first
			const conversations = (idbResponse.objects as Conversation[]).sort(
				(a, b) =>
					new Date(b.lastMessageDate as string).getTime() -
					new Date(a.lastMessageDate as string).getTime()
			);

			// Construct the API URL to fetch message status updates after the latest message date
			const url = `http://localhost:8000/updated-status?last_updated=${conversations[0].lastMessageDate}`;
			const response = await axios({
				method: "get",
				url: url,
				withCredentials: true,
			});

			console.log(response.data);

			// Process the response if the request is successful
			if (response.status === 200) {
				if (response.data.message_status_updates.length > 0) {
					// Map response data to message object
					const messages: Message[] =
						response.data.message_status_updates.map(
							(msg: object) => mapResponseToMessage(msg)
						);

					console.log(messages);

					// Store the updated message in indexedDB
					await indexedDbService.batchUpsert("message", messages);

					// Update the application state whith new messages
					messages.forEach((element) => {
						updateMessageInState(element);
					});
				}
			}
		}
	}

	return {
		syncAndLoadConversationsFromLastDate,
		sendMessage,
		syncMessageStatus,
		markMessageAsSeen,
	};
});
