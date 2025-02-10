export interface Message {
	id: string | null;
	conversationId: string | null;
	senderId: string | null;
	receiverId: string | null;
	message: string | null;
	attachment: FileInfo | null;
	sendingTime: string | null;
	receivedTime: string | null;
	seenTime: string | null;
	status: string | null;
}

export enum FileType {
	attachment = "attachment",
}

export interface FileInfo {
	type: FileType;
	key: string | null;
	tempFileId: string | null;
	size: number | null;
	name: string | null;
}

export function mapResponseToMessage(response: object): Message {
	const mapping = {
		id: "id",
		conversationId: "conversation_id",
		senderId: "sender_id",
		receiverId: "receiver_id",
		message: "message",
		attachment: "attachment",
		sendingTime: "sending_time",
		receivedTime: "received_time",
		seenTime: "seen_time",
		status: "status",
	};

	let message = {} as Message;

	for (const [key, path] of Object.entries(mapping)) {
		const value = (response as { [key: string]: any })[path];
		if (value) {
			if (key == "attachment") {
				message["attachment"] = value
					? ({
							type: value.type,
							name: value.name,
							key: value.key,
							tempFileId: value.temp_fileId,
							size: value.size,
					  } as FileInfo)
					: null;
			} else {
				message[key as keyof Message] = value;
			}
		} else {
			message[key as keyof Message] = null;
		}
	}

	return message;
}
