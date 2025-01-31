export interface Message {
	id: string | null;
	conversationId: string | null;
	senderId: string | null;
	receiverId: string | null;
	message: string | null;
	sendingTime: string | null;
	receivedTime: string | null;
	seenTime: string | null;
	status: string | null;
}

export function mapResponseToMessage(response: object): Message {
	const mapping = {
		id: "id",
		conversationId: "conversation_id",
		senderId: "sender_id",
		receiverId: "receiver_id",
		message: "message",
		sendingTime: "sending_time",
		receivedTime: "received_time",
		seenTime: "seen_time",
		status: "status",
	};

	let message = {} as Message;

	for (const [key, path] of Object.entries(mapping)) {
		const value = (response as { [key: string]: any })[path];
		if (value !== undefined) {
			message[key as keyof Message] = value;
		} else {
			message[key as keyof Message] = null;
		}
	}

	return message;
}
