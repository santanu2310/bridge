export interface Message {
	id: string;
	conversationId: string;
	senderId: string;
	recieverId: string | null;
	message: string;
	sendingTime: string | null;
	status: string;
}
