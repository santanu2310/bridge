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
