import { defineStore } from "pinia";
import { ref } from "vue";
import axios from "axios";

import { indexedDbService } from "@/services/indexDbServices";
import { mapResponseToUser, type User } from "@/types/User";
import { useUserStore } from "./user";
import type { Conversation } from "@/types/Conversation";
// import type { Message } from "@/types/Message";
import { mapResponseToMessage, type Message } from "@/types/Message";

export const useFriendStore = defineStore("friend", () => {
	const friends = ref<User[]>();

	const lastFriendsUpdate = localStorage.getItem("lastUpdated");

	const userStore = useUserStore();

	const { isOnline, setOnline, setOffline } =
		userStore.useOnlineStatusManager();

	async function listFriend() {
		try {
			const result: { newlyCreated: boolean; objects: User[] } =
				(await indexedDbService.getAllRecords("friends")) as {
					newlyCreated: boolean;
					objects: User[];
				};

			friends.value = result.objects;

			let url = "http://localhost:8000/friends/get-friends";

			// Add the lastupdated date
			if (!result.newlyCreated && lastFriendsUpdate) {
				url += `?updateAfter=${lastFriendsUpdate}`;
			}

			const response = await axios({
				method: "get",
				url: url,
				withCredentials: true,
			});

			if (response.status === 200) {
				const updatedFriend: User[] = await Promise.all(
					response.data.map(async (data: object) => {
						const user = mapResponseToUser(data);
						await indexedDbService.updateRecord("friends", user);

						return user;
					})
				);

				//update the original fiends
				if (friends.value) {
					const updatedFriendMap = new Map(
						updatedFriend.map((user) => [user.id, user])
					);
					friends.value.forEach((user: User) => {
						if (updatedFriendMap.has(user.id)) {
							Object.assign(user, updatedFriendMap.get(user.id)!);
						}
					});
				}

				localStorage.setItem("lastUpdated", new Date().toISOString());
			}

			friends.value.sort((a, b) => {
				const aName = a.fullName || "";
				const bName = b.fullName || "";
				return aName.localeCompare(bName);
			});
		} catch (error) {
			console.error(error);
		}
	}

	async function getConversation(userId: string): Promise<Message[] | null> {
		//checking in local database
		const conversation: Conversation = (await indexedDbService.getRecord(
			"conversation",
			null,
			{ participant: userId }
		)) as Conversation;

		// If conversation in local database
		if (conversation) {
			if (
				userStore.currentConversation?.receiverId ==
				conversation.participant
			) {
				userStore.currentConversation!.convId = conversation.id;
			}

			const request = indexedDbService.getAllRecords("message", {
				conversationId: conversation.id as string,
			});

			const oldMessages = (await request).objects as Message[];
			return oldMessages;
		} else {
			//retrive from server
			const response = await axios({
				method: "get",
				url: `http://localhost:8000/conversation/get-conversation?friend_id=${userId}`,
				withCredentials: true,
			});

			if (response.status == 200) {
				const convResponse: Conversation = {
					id: response.data.id,
					participant: response.data.participant,
					unseenMessageIds: response.data.unseen_message_ids,
					startDate: response.data.start_date,
					lastMessageDate: response.data.last_message_date,
				};

				//Add the conversation to indesedDb and to local variable
				await indexedDbService.addRecord("conversation", convResponse);
				if (
					userStore.currentConversation?.receiverId ==
					convResponse.participant
				) {
					userStore.currentConversation!.convId = convResponse.id;
				}

				//add the messages to the indesedDb
				const oldMessages = response.data.messages.map((msg: object) =>
					mapResponseToMessage(msg)
				);
				indexedDbService.batchInsert("message", oldMessages);

				return oldMessages;
			}

			return null;
		}
	}

	async function getInitialOnlineStatus() {
		try {
			// Make a GET request to fetch the list of online users
			const response = await axios({
				method: "get",
				url: "http://localhost:8000/conversation/online-users",
				withCredentials: true,
			});

			if (response.status === 200) {
				// Mark all friends as online
				for (const userId of response.data.online_friends) {
					setOnline(userId);
				}
			} else {
				console.warn("Unexpected response format or status:", response);
			}
		} catch (error) {
			console.error("Failed to fetch online friend : ", error);
		}
	}

	return { friends, getConversation, listFriend, getInitialOnlineStatus };
});
