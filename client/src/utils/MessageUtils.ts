import { toRaw } from "vue";
import { useUserStore } from "@/stores/user";
import { indexedDbService } from "@/services/indexDbServices";
import type { Message } from "@/types/Message";
import type { Conversation } from "@/types/Conversation";

export function updateMessageInState(message: Message, tempId?: string | null) {
	const userStore = useUserStore();

	// Check for conversation and messages
	const conversation =
		userStore.conversations[message.conversationId as string];
	if (!conversation || !conversation.messages) return;

	const messages = conversation.messages;
	const messageId = tempId ? tempId : message.id;

	// Update the message in the conversation variable
	for (let i = messages.length - 1; i >= 0; i--) {
		if (messages[i].id === messageId) {
			messages[i] = Object.assign({}, toRaw(messages[i]), message);
			break;
		}
	}
}

export function addMessageInState(message: Message, tempId?: string | null) {
	const userStore = useUserStore();

	// When the user is starting the conversation
	if (!message.conversationId) {
		// create a new inStateconversation
		userStore.conversations[message.id!] = {
			messages: [],
			isActive: true,
			participant: message.receiverId as string,
			lastMessageDate: message.sendingTime as string,
		};

		//Add the message
		userStore.conversations[message.id as string].messages.push(message);
	}
	// Message have conversation Id
	else {
		// Old message
		if (userStore.conversations[message.conversationId]) {
			userStore.conversations[message.conversationId].messages.push(
				message
			);
		}
		// New message initiated by other user
		else {
			userStore.conversations[message.conversationId] = {
				messages: [message],
				participant: message.senderId as string,
				lastMessageDate: message.sendingTime as string,
				isActive: true,
			};

			if (tempId) delete userStore.conversations[tempId];
		}

		// Update the temperory message with original message
		if (tempId) {
			updateMessageInState(message, tempId);
		}
	}
}

export function updateMessageInStateByTempId(message: Message) {}
