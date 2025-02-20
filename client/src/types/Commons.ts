export type PacketType =
	| "open"
	| "close"
	| "ping"
	| "pong"
	| "message"
	| "upgrade"
	| "noop"
	| "error";

export type RawData = any;

export interface Packet {
	type: PacketType;
	data?: RawData;
}

export interface UserBrief {
	id: string;
	username: string;
	full_name: string;
	bio: string | null;
	profile_picture: string | null;
}

export interface FriendRequest {
	type: string;
	id: string;
	user: UserBrief;
	message: string | null;
	status: string;
	created_time: string;
}
