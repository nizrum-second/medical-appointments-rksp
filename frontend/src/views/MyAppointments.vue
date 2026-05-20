<template>
	<div class="page-card">
		<h1 class="mb-6">Мои записи</h1>

		<div
			v-if="loading"
			class="text-center py-8">
			Загрузка...
		</div>
		<div
			v-else-if="appointmentsStore.appointments.length === 0"
			class="text-center py-8 text-slate-500">
			Записи не найдены
		</div>
		<div
			v-else
			class="space-y-4">
			<AppointmentCard
				v-for="appointment in appointmentsStore.appointments"
				:key="appointment.id"
				:appointment="appointment"
				:show-cancel="appointment.status === 'scheduled'"
				@cancel="cancelAppointment(appointment.id)" />
		</div>
	</div>
</template>

<script setup>
	import { ref, onMounted } from "vue";
	import { useAppointmentsStore } from "../stores/appointments";
	import AppointmentCard from "../components/AppointmentCard.vue";

	const appointmentsStore = useAppointmentsStore();
	const loading = ref(true);

	const cancelAppointment = async (appointmentId) => {
		if (confirm("Вы уверены, что хотите отменить запись?")) {
			const result =
				await appointmentsStore.cancelAppointment(appointmentId);
			if (!result.success) {
				alert(result.error);
			}
		}
	};

	onMounted(async () => {
		await appointmentsStore.getMyAppointments();
		loading.value = false;
	});
</script>
