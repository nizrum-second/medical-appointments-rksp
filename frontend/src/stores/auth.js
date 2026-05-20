import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "../services/api";
import router from "../router";

export const useAuthStore = defineStore("auth", () => {
	const user = ref(null);
	const token = ref(localStorage.getItem("access_token") || null);

	const isAuthenticated = computed(() => !!token.value);
	const userRole = computed(() => user.value?.role);

	const login = async (credentials) => {
		try {
			const response = await api.post("/auth/login", credentials);
			token.value = response.data.access_token;
			localStorage.setItem("access_token", token.value);
			await fetchUser();
			return { success: true };
		} catch (error) {
			return {
				success: false,
				error: error.response?.data?.detail || "Login failed",
			};
		}
	};

	const register = async (userData) => {
		try {
			const response = await api.post("/auth/register", userData);
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error: error.response?.data?.detail || "Registration failed",
			};
		}
	};

	const fetchUser = async () => {
		try {
			const response = await api.get("/auth/me");
			user.value = response.data;
		} catch (error) {
			console.error("Failed to fetch user:", error);
			logout();
		}
	};

	const logout = () => {
		user.value = null;
		token.value = null;
		localStorage.removeItem("access_token");
		router.push("/login");
	};

	const updateProfile = async (userData) => {
		try {
			const response = await api.put("/auth/me", userData);
			user.value = response.data;
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error: error.response?.data?.detail || "Update failed",
			};
		}
	};

	return {
		user,
		token,
		isAuthenticated,
		userRole,
		login,
		register,
		fetchUser,
		logout,
		updateProfile,
	};
});
