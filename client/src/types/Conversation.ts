export interface Conversation {
	id: string;
	participant: string;
	unseenMessage_ids: string[];
	startDate: string | null;
	lastMessageDate: string | null;
}
