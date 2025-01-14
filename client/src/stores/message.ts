import { defineStore } from "pinia";
import { ref } from "vue";
import { indexedDbService } from "@/services/indexDbServices";
import type { Message } from "@/types/Message";
import type { Conversation } from "@/types/Conversation";
import { useUserStore } from "./user";

export const useMessageStore = defineStore("message", () => {
	const socket = new WebSocket("ws://localhost:8000/chat/socket");

	const conversations = ref<{
		[key: string]: {
			messages: Message[];
			participant: string;
			lastMessageDate: string;
			isActive: boolean;
		};
	}>({});
	const userStore = useUserStore();

	//data for current going conversation
	const currentConversation = ref<{
		convId: string | null;
		receiverId: string | null;
	} | null>(null);

	//handle receiving message
	socket.onmessage = async (event) => {
		const msg = JSON.parse(event.data);

		// Validate required field
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
			receiverId: msg.receiver_id,
			message: msg.message,
			sendingTime: msg.sending_time,
			status: msg.status,
		};

		//check for conversation in indesedDb
		const conversation: Conversation = (await indexedDbService.getRecord(
			"conversation",
			message.conversationId
		)) as Conversation;

		//when the conversation is new
		if (!conversation) {
			const newConversation: Conversation = {
				id: message.conversationId,
				participant: message.senderId,
				unseenMessageIds: [message.id as string],
				startDate: null,
				lastMessageDate: message.sendingTime,
			};

			//TODO: a function to retrive all info about the conversation and update the indesed db

			conversations.value[message.conversationId as string] = {
				isActive: true,
				messages: [],
				lastMessageDate: message.sendingTime as string,
				participant: message.senderId as string,
			};

			await indexedDbService.addRecord("conversation", newConversation);
		} else {
			// For recent conversation
			if (
				currentConversation.value == null ||
				currentConversation.value.convId != message.conversationId
			) {
				conversation.unseenMessageIds!.push(message.id as string);
			}
			// Ongoing conversation
			else {
				// message.status = "read";
				//TODO: A function to send server this information
			}

			// Update the last conversation datetime
			conversations.value[message.conversationId!].lastMessageDate =
				message.sendingTime as string;

			conversation.lastMessageDate = message.sendingTime;
			await indexedDbService.updateRecord("conversation", conversation);
		}

		// Remove temp messagee(only for the sender)
		if (message.senderId == userStore.user.id) {
			if (msg.temp_id) {
				await indexedDbService.deleteRecord("message", msg.temp_id);
				deleteMessageFromList(message.conversationId!, msg.temp_id);
			}
		}

		// Append the new message to the current conversation
		conversations.value[message.conversationId!].messages.push(message);

		// Store the message in IndexedDB
		await indexedDbService.addRecord("message", message);
	};

	async function sendMessage(message: string) {
		if (!currentConversation.value) {
			return;
		}
		if (
			currentConversation.value.convId == null &&
			currentConversation.value.receiverId == null
		) {
			console.error("Both conversationId and receiverId are null");
			return;
		}

		const msg = {
			message: message,
			receiver_id: currentConversation.value.receiverId,
			conversation_id: currentConversation.value.convId,
			temp_id: crypto.randomUUID(),
		};

		// Make the data ready for indexedDb and add it
		const iDbMessage: Message = {
			id: msg.temp_id.toString(),
			senderId: userStore.user.id,
			receiverId: msg.receiver_id,
			conversationId: msg.conversation_id,
			message: msg.message,
			sendingTime: new Date().toISOString(),
			status: "pending",
		};
		await indexedDbService.addRecord("message", iDbMessage);

		if (!currentConversation.value.convId) {
			//New conversation
			conversations.value[msg.temp_id] = {
				messages: [],
				isActive: true,
				participant: msg.receiver_id as string,
				lastMessageDate: new Date().toISOString(),
			};
			conversations.value[msg.temp_id].messages.push(iDbMessage);
		} else {
			// Old conversation
			conversations.value[
				currentConversation.value.convId
			]?.messages.push(iDbMessage);
		}

		socket.send(JSON.stringify(msg));
	}

	function deleteMessageFromList(
		convId: string,
		targetedId: string,
		candidateIndex = -1
	) {
		// Set candidateIndex to the last element on the first call
		if (candidateIndex === -1) {
			candidateIndex = conversations.value[convId].messages.length - 1;
		}

		// Base case: stop if candidateIndex is less than 0
		if (candidateIndex < 0) {
			return;
		}
		if (
			conversations.value[convId].messages[candidateIndex].id ==
			targetedId
		) {
			conversations.value[convId].messages.splice(candidateIndex, 1);
			return;
		}
		return deleteMessageFromList(convId, targetedId, candidateIndex - 1);
	}

	return { currentConversation, conversations, sendMessage };
});
