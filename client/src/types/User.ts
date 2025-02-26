export interface User {
	id: string;
	userName: string;
	fullName: string;
	email: string;
	bio: string | null;
	profilePicUrl: string | null;
	location: string | null;
	joinedDate: string | null;
}

export function mapResponseToUser(response: object): User {
	const mapping = {
		id: "id",
		userName: "username",
		fullName: "full_name",
		email: "email",
		bio: "bio",
		location: "location",
		profilePicUrl: "profile_picture",
		joinedDate: "created_at",
	};

	let user = {} as User;

	for (const [key, path] of Object.entries(mapping)) {
		const value = (response as { [key: string]: any })[path];
		if (value) {
			user[key as keyof User] = value;
		} else {
			if (["id", "userName", "fullName", "email"].includes(key)) {
				throw new Error(`Missing required value for key: ${key}`);
			}
			// user[key as keyof User] = null;
			else (user as any)[key] = null;
		}
	}

	return user;
}
