import { EventEmitter } from "events";
import type { PacketType, RawData, Packet } from "@/types/Commons";

type ReadyState = "opening" | "open" | "closing" | "closed";

export class Socket extends EventEmitter {
	private url: string;
	private socket: WebSocket | null = null;
	private heartbeatInterval: number = 30000;
	private pingTimeoutTimer: number | null;
	private pingIntervalTimer: number | null;

	private pingTimeout: number = 20000;
	private pingInterval: number = 25000;

	public _readyState: ReadyState = "opening";

	get readyState() {
		return this._readyState;
	}

	set readyState(state: ReadyState) {
		this._readyState = state;
	}

	constructor(url: string) {
		super();
		this.url = url;
		this.pingIntervalTimer = null;
		this.pingTimeoutTimer = null;
	}

	connect(): void {
		if (this.readyState === "open") {
			console.warn("Socket is open.");
			return;
		}
		this.socket = new WebSocket(this.url);

		this.socket.onopen = () => {
			this.readyState = "open";
			this.schedulePing();
		};

		this.socket.onclose = this.onClose.bind(this);

		this.socket.onerror = (error) => {
			console.error("WebSocket error:", error);
			this.emit("error", error);
		};

		this.socket.onmessage = (event: MessageEvent) => {
			if ("open" !== this.readyState) {
				console.debug("packet received with closed socket");
				return;
			}

			const data = JSON.parse(event.data);

			switch (data.type) {
				case "pong":
					if (this.pingTimeoutTimer)
						clearTimeout(this.pingTimeoutTimer);
					this.schedulePing();
					break;

				case "message":
					this.emit("message", data.data);
					break;

				default:
					console.warn("Unknown packet type: ", data.type);
			}
		};
	}

	private schedulePing() {
		this.pingIntervalTimer = setTimeout(() => {
			this.sendMessage("ping");
			this.resetPingTimeout();
		}, this.pingInterval);
	}

	private resetPingTimeout() {
		this.pingTimeoutTimer = setTimeout(() => {
			if (this.readyState === "closed") this.connect();
			this.socket?.close();
		}, this.pingTimeout);
	}

	public send(data: RawData) {
		this.sendMessage("message", data);
		return this;
	}

	private sendMessage(type: PacketType, data?: RawData) {
		if ("closing" !== this.readyState && "closed" !== this.readyState) {
			const packet: Packet = {
				type,
			};

			if (data) packet.data = data;
			this.socket?.send(JSON.stringify(packet));
		}
	}

	private onClose() {
		this.readyState = "closed";
		console.info("connection is closed - Opening in 5 sec");

		if (this.pingIntervalTimer !== null) {
			clearTimeout(this.pingIntervalTimer);
			this.pingIntervalTimer = null;
		}

		if (this.pingTimeoutTimer !== null) {
			clearTimeout(this.pingTimeoutTimer);
			this.pingTimeoutTimer = null;
		}

		this.pingIntervalTimer = null;
		this.pingTimeoutTimer = null;

		setTimeout(() => {
			this.connect();
		}, 5000);
	}
}
