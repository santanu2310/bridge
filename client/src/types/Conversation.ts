export interface Conversation {
	id: string | null;
	participant: string | null;
	unseenMessageIds: string[] | null;
	startDate: string | null;
	lastMessageDate: string | null;
}
