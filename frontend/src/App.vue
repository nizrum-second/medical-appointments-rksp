<template>
	<div
		id="app"
		class="min-h-screen bg-gradient-to-b from-slate-100 to-slate-200">
		<Navbar v-if="authStore.isAuthenticated" />
		<main
			:class="{
				'mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8':
					authStore.isAuthenticated,
			}">
			<router-view v-if="!loading" />
			<LoadingSpinner v-else />
		</main>
	</div>
</template>

<script setup>
	import { ref, onMounted, watch } from "vue";
	import { useAuthStore } from "./stores/auth";
	import { useRouter } from "vue-router";
	import Navbar from "./components/Navbar.vue";
	import LoadingSpinner from "./components/LoadingSpinner.vue";

	const authStore = useAuthStore();
	const router = useRouter();
	const loading = ref(true);

	const redirectToDashboard = () => {
		if (authStore.isAuthenticated && authStore.user) {
			const currentPath = router.currentRoute.value.path;

			if (currentPath === "/" || currentPath === "/dashboard") {
				if (authStore.userRole === "admin") {
					router.push("/admin");
				} else if (authStore.userRole === "doctor") {
					router.push("/doctor-dashboard");
				} else {
					router.push("/dashboard");
				}
			}
		}
	};

	onMounted(async () => {
		if (authStore.isAuthenticated) {
			await authStore.fetchUser();
		}
		loading.value = false;
		redirectToDashboard();
	});

	watch(
		() => authStore.user,
		() => {
			redirectToDashboard();
		},
	);
</script>
