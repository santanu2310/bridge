export function formatDateDifference(
	targetDate: string,
	exatDate: boolean = true
): string {
	const moment = new Date();
	const inpDate = new Date(targetDate);

	const dayNames = [
		"Sunday",
		"Monday",
		"Tuesday",
		"Wednesday",
		"Thursday",
		"Friday",
		"Saturday",
	];

	if (
		moment.getFullYear() - inpDate.getFullYear() === 0 &&
		moment.getMonth() - inpDate.getMonth() === 0
	) {
		const dateDiff = moment.getDate() - inpDate.getDate();
		//for same day message
		if (dateDiff === 0) {
			if (!exatDate) return "today";
			const time =
				inpDate.getHours().toString().padStart(2, "0") +
				":" +
				inpDate.getMinutes().toString().padStart(2, "0");
			return time;
		} else if (dateDiff === 1) {
			return "yesterday";
		} else if (dateDiff < 7) {
			return dayNames[inpDate.getDay()];
		} else {
			return `${inpDate.getDate().toString().padStart(2, "0")}/${(
				inpDate.getMonth() + 1
			)
				.toString()
				.padStart(2, "0")}/${inpDate.getFullYear()}`;
		}
	} else {
		return `${inpDate.getDate().toString().padStart(2, "0")}/${(
			inpDate.getMonth() + 1
		)
			.toString()
			.padStart(2, "0")}/${inpDate.getFullYear()}`;
	}
}
