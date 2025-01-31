export enum MessageStatus {
	send = "send",
	received = "received",
	seen = "seen",
}

export enum SyncMessageType {
	MessageStatus = "message_status",
}

export interface MessageEvent {
	message_id: string;
	timestamp: string;
}

export interface MessageStatusUpdate {
	type: SyncMessageType;
	data: MessageEvent[];
	status: MessageStatus;
}
