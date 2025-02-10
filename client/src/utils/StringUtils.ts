export function getInitials(name: string) {
	const sArray = name.split(" ").map((word) => word.charAt(0).toUpperCase());
	return sArray[0] + sArray[sArray.length - 1];
}

export function getFileExtension(file: File): string {
	const fileName = file.name;
	const lastDotIndex = fileName.lastIndexOf(".");

	// Return an empty string if no dot is found (no extension)
	if (lastDotIndex === -1) {
		return "";
	}

	// Extract and return the extension (everything after the last dot)
	return fileName.substring(lastDotIndex + 1).toLowerCase();
}

export function formatFileSize(size: number): string {
	const sizeInKB = size / 1024;
	if (sizeInKB > 1024) {
		return (sizeInKB / 1024).toFixed(1).toString() + " MB";
	}

	return sizeInKB.toFixed(1).toString() + " KB";
}

export function removeExtension(name: string) {
	const dotIndex = name.lastIndexOf(".");
	return dotIndex !== -1 ? name.substring(0, dotIndex) : name;
}
