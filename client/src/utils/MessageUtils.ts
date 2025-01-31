import type { Message } from "@/types/Message";
import { useUserStore } from "@/stores/user";
import { toRaw } from "vue";

export function updateMessageInState(message: Message) {
	const userStore = useUserStore();

	// Check for conversation and messages
	const conversation =
		userStore.conversations[message.conversationId as string];
	if (!conversation || !conversation.messages) return;

	const messages = conversation.messages;

	// Update the message in the conversation variable
	for (let i = messages.length - 1; i >= 0; i--) {
		if (messages[i].id === message.id) {
			messages[i] = Object.assign({}, toRaw(messages[i]), message);
			break;
		}
	}
}
