import { defineStore } from "pinia";
import { indexedDbService } from "@/services/indexDbServices";
import { Socket } from "@/services/socektServices";
import { type Message, mapResponseToMessage } from "@/types/Message";
import type { Conversation } from "@/types/Conversation";
import {
	type MessageStatusUpdate,
	MessageStatus,
	SyncMessageType,
} from "@/types/SocketEvents";
import { useUserStore } from "./user";
import { useSyncStore } from "./background_sync";

export const useMessageStore = defineStore("message", () => {
	const socket = new Socket("ws://localhost:8000/chat/socket");
	socket.connect();

	const userStore = useUserStore();
	const syncStore = useSyncStore();

	//handle receiving message
	socket.on("message", async (msg) => {
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

		const message = mapResponseToMessage(msg);

		// Store the message in IndexedDB
		await indexedDbService.addRecord("message", message);

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

			userStore.conversations[message.conversationId as string] = {
				isActive: true,
				messages: [],
				lastMessageDate: message.sendingTime as string,
				participant: message.senderId as string,
			};

			await indexedDbService.addRecord("conversation", newConversation);
		} else {
			// For recent conversation
			if (
				userStore.currentConversation == null ||
				userStore.currentConversation.convId != message.conversationId
			) {
				conversation.unseenMessageIds!.push(message.id as string);
			}
			// Ongoing conversation
			else {
				// message.status = "read";
				//TODO: A function to send server this information
			}

			// Update the last conversation datetime
			userStore.conversations[message.conversationId!].lastMessageDate =
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
		} else {
			// Send acknowledgement to server that the message is being received
			const now = new Date().toISOString();
			const syncMessge: MessageStatusUpdate = {
				type: SyncMessageType.MessageStatus,
				data: [
					{
						message_id: message.id as string,
						timestamp: now,
					},
				],
				status: MessageStatus.received,
			};

			syncStore.sendMessage(syncMessge);
		}

		// Append the new message to the current conversation
		userStore.conversations[message.conversationId!].messages.push(message);
	});

	async function sendMessage(message: string) {
		if (!userStore.currentConversation) {
			return;
		}
		if (
			userStore.currentConversation.convId == null &&
			userStore.currentConversation.receiverId == null
		) {
			console.error("Both conversationId and receiverId are null");
			return;
		}

		const msg = {
			message: message,
			receiver_id: userStore.currentConversation.receiverId,
			conversation_id: userStore.currentConversation.convId,
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
			receivedTime: null,
			seenTime: null,
		};
		await indexedDbService.addRecord("message", iDbMessage);

		if (!userStore.currentConversation.convId) {
			//New conversation
			userStore.conversations[msg.temp_id] = {
				messages: [],
				isActive: true,
				participant: msg.receiver_id as string,
				lastMessageDate: new Date().toISOString(),
			};
			userStore.conversations[msg.temp_id].messages.push(iDbMessage);
		} else {
			// Old conversation
			userStore.conversations[
				userStore.currentConversation.convId
			]?.messages.push(iDbMessage);
		}

		socket.send(msg);
	}

	function deleteMessageFromList(
		convId: string,
		targetedId: string,
		candidateIndex = -1
	) {
		// Set candidateIndex to the last element on the first call
		if (candidateIndex === -1) {
			candidateIndex =
				userStore.conversations[convId].messages.length - 1;
		}

		// Base case: stop if candidateIndex is less than 0
		if (candidateIndex < 0) {
			return;
		}
		if (
			userStore.conversations[convId].messages[candidateIndex].id ==
			targetedId
		) {
			userStore.conversations[convId].messages.splice(candidateIndex, 1);
			return;
		}
		return deleteMessageFromList(convId, targetedId, candidateIndex - 1);
	}

	return { sendMessage };
});
