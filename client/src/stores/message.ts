import { defineStore } from "pinia";
import { ref } from "vue";
import { indexedDbService } from "@/services/indexDbServices";
import type { Message } from "@/types/Message";
import type { Conversation } from "@/types/Conversation";
import type { User } from "@/types/User";

export const useMessageStore = defineStore("message", () => {
	const socket = new WebSocket("ws://localhost:8000/chat/socket");
	const conversations = ref<{ [key: string]: Message[] }>({});

	//data for current going conversation
	const currentConversation = ref<{
		convId: string | null;
		recieverId: string | null;
	} | null>(null);

	//handle receiving message
	socket.onmessage = async (event) => {
		const msg = JSON.parse(event.data);
		console.log(msg);
		// Check for required fields in `msg` before proceeding
		if (
			!msg.id ||
			!msg.conversation_id ||
			!msg.sender_id ||
			!msg.message ||
			!msg.sending_time ||
			!msg.status
		) {
			console.error("Invalid message data:", msg);
			return;
		}

		//Map the message data to the message variable
		const message: Message = {
			id: msg.id,
			conversationId: msg.conversation_id,
			senderId: msg.sender_id,
			recieverId: msg.reciever_id,
			message: msg.message,
			sendingTime: msg.sending_time,
			status: msg.status,
		};

		//TODO: first check the conversation in conversations
		const conversation: Conversation = (await indexedDbService.getRecord(
			"conversation",
			message.conversationId
		)) as Conversation;

		//when the conversation is new
		if (!conversation) {
			const newConversation: Conversation = {
				id: message.conversationId,
				participant: message.senderId,
				unseenMessage_ids: [],
				startDate: null,
				lastMessageDate: message.sendingTime,
			};

			await indexedDbService.addRecord("conversation", newConversation);

			conversations.value[message.conversationId] = [];

			//the message if of current conv
			if (
				currentConversation.value &&
				message.senderId == currentConversation.value.recieverId
			) {
				currentConversation.value.convId = message.conversationId;
			}
		}

		if (
			currentConversation.value == null ||
			currentConversation.value.convId != message.conversationId
		) {
			// this in another conversations
			// retrive the conversation, add the unseen message id and put it back
			const conversation: Conversation =
				(await indexedDbService.getRecord(
					"conversation",
					message.conversationId
				)) as Conversation;

			conversation.unseenMessage_ids.push(message.id);
			await indexedDbService.updateRecord("conversation", conversation);
		}

		conversations.value[message.conversationId].push(message);

		await indexedDbService.deleteRecord("message", msg.temp_id);
		await indexedDbService.addRecord("message", message);
	};

	async function sendMessage(
		message: string
		// conversationId: string | null = null,
		// recieverId: string | null = null
	) {
		if (!currentConversation.value) {
			return;
		}
		if (
			currentConversation.value.convId == null &&
			currentConversation.value.recieverId == null
		) {
			console.log(currentConversation.value.recieverId);
			console.error("Both conversationId and recieverId are null");
			return;
		}

		const msg = {
			message: message,
			reciever_id: currentConversation.value.recieverId,
			conversation_id: currentConversation.value.convId,
			temp_id: crypto.randomUUID(),
		};

		const idbData = {
			id: msg.temp_id,
			message: msg.message,
			recieverId: msg.reciever_id,
			conversationId: msg.conversation_id,
		};

		const idbResult = await indexedDbService.addRecord("message", idbData);
		console.log(idbResult);

		socket.send(JSON.stringify(msg));
	}

	return { currentConversation, conversations, sendMessage };
});
