export const formatDate = (datetime) => {
	if (!datetime) return "—";
	try {
		const date = new Date(datetime);
		if (isNaN(date.getTime())) return "—";
		return date.toLocaleDateString("ru-RU");
	} catch (e) {
		return "—";
	}
};

export const formatTime = (datetime) => {
	if (!datetime) return "—";
	try {
		const date = new Date(datetime);
		if (isNaN(date.getTime())) return "—";
		return date.toLocaleTimeString("ru-RU", {
			hour: "2-digit",
			minute: "2-digit",
		});
	} catch (e) {
		return "—";
	}
};

export const formatDateTime = (datetime) => {
	if (!datetime) return "—";
	try {
		const date = new Date(datetime);
		if (isNaN(date.getTime())) return "—";
		return date.toLocaleString("ru-RU");
	} catch (e) {
		return "—";
	}
};
