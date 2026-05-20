<template>
	<div class="space-y-6">
		<div class="page-card">
			<h1 class="mb-4">
				Добро пожаловать, {{ authStore.user?.full_name }}
			</h1>
			<p class="text-slate-600">
				Ваша роль:
				<span class="font-semibold">
					{{ roleText }}
				</span>
			</p>
		</div>

		<div class="grid md:grid-cols-2 gap-6">
			<div class="page-card">
				<h2 class="text-xl font-semibold mb-4">Быстрые действия</h2>
				<div class="space-y-3">
					<router-link
						to="/doctors"
						class="btn-primary block text-center">
						Записаться на прием
					</router-link>
					<router-link
						to="/my-appointments"
						class="btn-secondary block text-center">
						Мои записи
					</router-link>
				</div>
			</div>

			<div class="page-card">
				<h2 class="text-xl font-semibold mb-4">Последние записи</h2>
				<div
					v-if="loading"
					class="text-center py-4">
					Загрузка...
				</div>
				<div
					v-else-if="recentAppointments.length === 0"
					class="text-slate-500 text-center py-4">
					Нет записей
				</div>
				<div
					v-else
					class="space-y-3">
					<AppointmentCard
						v-for="appointment in recentAppointments"
						:key="appointment.id"
						:appointment="appointment" />
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
	import { ref, computed, onMounted } from "vue";
	import { useAuthStore } from "../stores/auth";
	import { useAppointmentsStore } from "../stores/appointments";
	import { useRouter } from "vue-router";
	import AppointmentCard from "../components/AppointmentCard.vue";

	const authStore = useAuthStore();
	const appointmentsStore = useAppointmentsStore();
	const loading = ref(true);
	const router = useRouter();

	if (authStore.userRole !== "patient") {
		if (authStore.userRole === "admin") {
			router.push("/admin");
		} else if (authStore.userRole === "doctor") {
			router.push("/doctor-dashboard");
		}
	}

	const roleText = computed(() => {
		const roles = {
			patient: "Пациент",
			doctor: "Врач",
			admin: "Администратор",
		};
		return roles[authStore.userRole] || authStore.userRole;
	});

	const recentAppointments = computed(() => {
		return appointmentsStore.appointments.slice(0, 3);
	});

	onMounted(async () => {
		if (authStore.userRole === "patient") {
			await appointmentsStore.getMyAppointments();
		}
		loading.value = false;
	});
</script>
