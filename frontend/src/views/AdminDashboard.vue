<template>
	<div class="space-y-6">
		<div class="page-card">
			<h1 class="mb-2">Панель администратора</h1>
			<p class="text-slate-600">
				Добро пожаловать, {{ authStore.user?.full_name }}
			</p>
		</div>

		<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
			<div class="page-card text-center">
				<h3 class="text-lg font-semibold mb-2">Пользователи</h3>
				<router-link
					to="/admin/users"
					class="text-sm font-medium text-blue-700 hover:text-blue-900"
					>Управление пользователями →</router-link
				>
			</div>
			<div class="page-card text-center">
				<h3 class="text-lg font-semibold mb-2">Врачи</h3>
				<router-link
					to="/admin/doctors"
					class="text-sm font-medium text-blue-700 hover:text-blue-900"
					>Управление врачами →</router-link
				>
			</div>
			<div class="page-card text-center">
				<h3 class="text-lg font-semibold mb-2">Записи</h3>
				<router-link
					to="/admin/appointments"
					class="text-sm font-medium text-blue-700 hover:text-blue-900"
					>Управление записями →</router-link
				>
			</div>
			<div class="page-card text-center">
				<h3 class="text-lg font-semibold mb-2">Услуги</h3>
				<router-link
					to="/admin/services"
					class="text-sm font-medium text-blue-700 hover:text-blue-900"
					>Управление услугами →</router-link
				>
			</div>
		</div>
	</div>
</template>

<script setup>
	import { useAuthStore } from "../stores/auth";

	const authStore = useAuthStore();
</script>
