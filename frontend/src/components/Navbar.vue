<template>
	<nav
		class="sticky top-0 z-40 border-b border-slate-200 bg-white/95 text-slate-700 shadow-sm backdrop-blur">
		<div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
			<div class="flex justify-between items-center py-4">
				<div class="text-lg font-semibold tracking-tight text-slate-900">
					<router-link
						:to="homeRoute"
						class="rounded-md px-2 py-1 hover:bg-slate-100">
						Система управления онлайн-записями пациентов
					</router-link>
				</div>

				<button
					@click="mobileMenuOpen = !mobileMenuOpen"
					class="lg:hidden flex flex-col items-center justify-center w-10 h-10 rounded-lg border border-slate-300 hover:bg-slate-100 transition">
					<span class="block w-6 h-0.5 bg-slate-700 mb-1.5"></span>
					<span class="block w-6 h-0.5 bg-slate-700 mb-1.5"></span>
					<span class="block w-6 h-0.5 bg-slate-700"></span>
				</button>

				<div class="hidden lg:flex lg:items-center lg:space-x-4">
					<MenuItems @click="mobileMenuOpen = false" />
					<button
						@click="logout"
						class="btn-secondary ml-4">
						Выйти
					</button>
				</div>
			</div>

			<div
				v-if="mobileMenuOpen"
				class="lg:hidden py-4 border-t border-slate-200">
				<div class="flex flex-col space-y-3">
					<MenuItems @click="mobileMenuOpen = false" />
					<button
						@click="logout"
						class="btn-secondary w-full justify-start">
						Выйти
					</button>
				</div>
			</div>
		</div>
	</nav>
</template>

<script setup>
	import { computed, ref } from "vue";
	import { useAuthStore } from "../stores/auth";
	import { useRouter } from "vue-router";
	import MenuItems from "./MenuItems.vue";

	const authStore = useAuthStore();
	const router = useRouter();
	const mobileMenuOpen = ref(false);

	const homeRoute = computed(() => {
		if (authStore.userRole === "admin") return "/admin";
		if (authStore.userRole === "doctor") return "/doctor-dashboard";
		return "/dashboard";
	});

	const logout = () => {
		authStore.logout();
		router.push("/login");
	};
</script>
