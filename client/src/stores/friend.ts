import { defineStore } from "pinia";
import { reactive } from "vue";
import axios from "axios";

import { indexedDbService } from "@/services/indexDbServices";
import { mapResponseToUser, type User } from "@/types/User";
import { useMessageStore } from "./message";
import type { Conversation } from "@/types/Conversation";
// import type { Message } from "@/types/Message";
import { mapResponseToMessage, type Message } from "@/types/Message";

export const useFriendStore = defineStore("friend", () => {
	const friends = reactive<User[]>([]);

	const messageStore = useMessageStore();

	async function listFriend() {
		try {
			const result: { newlyCreated: boolean; objects: User[] } =
				(await indexedDbService.getAllRecords("friends")) as {
					newlyCreated: boolean;
					objects: User[];
				};

			console.log(result);

			if (result.newlyCreated) {
				const response = await axios({
					method: "get",
					url: "http://localhost:8000/friends/get-friends",
					withCredentials: true,
				});

				if (response.status === 200) {
					response.data.forEach((user: User) => {
						indexedDbService.addRecord(
							"friends",
							mapResponseToUser(user)
						);
					});
					friends.splice(
						0,
						friends.length,
						...response.data.map(mapResponseToUser)
					);
					console.log(friends);
					return;
				}
			} else friends.splice(0, friends.length, ...result.objects);

			friends.sort((a, b) => {
				const aName = a.fullName || "";
				const bName = b.fullName || "";
				return aName.localeCompare(bName);
			});
		} catch (error) {}
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
				messageStore.currentConversation?.receiverId ==
				conversation.participant
			) {
				messageStore.currentConversation!.convId = conversation.id;
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
				url: `http://localhost:8000/friends/get-conversation?friend_id=${userId}`,
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
					messageStore.currentConversation?.receiverId ==
					convResponse.participant
				) {
					messageStore.currentConversation!.convId = convResponse.id;
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

	listFriend();

	return { friends, getConversation, listFriend };
});
