import { defineStore } from "pinia";
import { reactive } from "vue";
import axios from "axios";

import { indexedDbService } from "@/services/indexDbServices";
import { mapResponseToUser, type User } from "@/types/User";
import { useMessageStore } from "./message";

export const useFriendStore = defineStore("friend", () => {
	const friends = reactive<User[]>([]);

	const messageStore = useMessageStore();

	async function listFriend() {
		try {
			const result: { newlyCreated: boolean; friends: User[] } =
				(await indexedDbService.getAllRecords("friends")) as {
					newlyCreated: boolean;
					friends: User[];
				};

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
					return;
				}
			} else friends.splice(0, friends.length, ...result.friends);

			friends.sort((a, b) => {
				const aName = a.fullName || "";
				const bName = b.fullName || "";
				return aName.localeCompare(bName);
			});
		} catch (error) {}
	}

	async function getConversations(userId: string) {
		//check in the conversation variable

		//checking in local database
		const conversation = await indexedDbService.getRecord(
			"conversation",
			null,
			{ participant: userId }
		);

		//retrive from server

		console.log(conversation);
	}

	listFriend();

	return { friends, getConversations };
});
