export interface User {
	id: string | null;
	userName: string | null;
	fullName: string | null;
	email: string | null;
	bio: string | null;
	profilePicUrl: string | null;
	joinedDate: string | null;
}

export function mapResponseToUser(response: object): User {
	const mapping = {
		id: "id",
		userName: "username",
		fullName: "full_name",
		email: "email",
		bio: "bio",
		profilePicUrl: "profile_picture",
		joinedDate: "created_at",
	};

	let user = {} as User;

	for (const [key, path] of Object.entries(mapping)) {
		const value = (response as { [key: string]: any })[path];
		if (value !== undefined) {
			user[key as keyof User] = value;
		} else {
			user[key as keyof User] = null;
		}
	}

	return user;
}
