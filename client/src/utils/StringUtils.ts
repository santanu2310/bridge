export function getInitials(name: string) {
	const sArray = name.split(" ").map((word) => word.charAt(0).toUpperCase());
	return sArray[0] + sArray[sArray.length - 1];
}
