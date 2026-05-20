<template>
	<div>
		<template v-if="authStore.userRole === 'patient'">
			<router-link
				to="/services"
				class="block rounded-lg px-3 py-2 text-sm font-medium hover:bg-slate-100 lg:inline-block"
				@click="$emit('click')">
				Все услуги
			</router-link>
			<router-link
				to="/doctors"
				class="block rounded-lg px-3 py-2 text-sm font-medium hover:bg-slate-100 lg:inline-block"
				@click="$emit('click')">
				Записаться к врачу
			</router-link>
			<router-link
				to="/my-appointments"
				class="block rounded-lg px-3 py-2 text-sm font-medium hover:bg-slate-100 lg:inline-block"
				@click="$emit('click')">
				Мои записи
			</router-link>
		</template>

		<template v-if="authStore.userRole === 'doctor'">
			<router-link
				to="/doctor-dashboard"
				class="block rounded-lg px-3 py-2 text-sm font-medium hover:bg-slate-100 lg:inline-block"
				@click="$emit('click')">
				Панель врача
			</router-link>
			<router-link
				to="/doctor-schedule"
				class="block rounded-lg px-3 py-2 text-sm font-medium hover:bg-slate-100 lg:inline-block"
				@click="$emit('click')">
				Расписание
			</router-link>
		</template>

		<template v-if="authStore.userRole === 'admin'">
			<router-link
				to="/admin"
				class="block rounded-lg px-3 py-2 text-sm font-medium hover:bg-slate-100 lg:inline-block"
				@click="$emit('click')">
				Панель администратора
			</router-link>
			<router-link
				to="/admin/users"
				class="block rounded-lg px-3 py-2 text-sm font-medium hover:bg-slate-100 lg:inline-block"
				@click="$emit('click')">
				Пользователи
			</router-link>
			<router-link
				to="/admin/doctors"
				class="block rounded-lg px-3 py-2 text-sm font-medium hover:bg-slate-100 lg:inline-block"
				@click="$emit('click')">
				Врачи
			</router-link>
			<router-link
				to="/admin/appointments"
				class="block rounded-lg px-3 py-2 text-sm font-medium hover:bg-slate-100 lg:inline-block"
				@click="$emit('click')">
				Записи
			</router-link>
			<router-link
				to="/admin/services"
				class="block rounded-lg px-3 py-2 text-sm font-medium hover:bg-slate-100 lg:inline-block"
				@click="$emit('click')">
				Услуги
			</router-link>
		</template>
	</div>
</template>

<script setup>
	import { useAuthStore } from "../stores/auth";

	const authStore = useAuthStore();

	defineEmits(["click"]);
</script>
