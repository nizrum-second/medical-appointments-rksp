<template>
	<div class="page-card">
		<h1 class="mb-6">Запись на прием</h1>

		<div
			v-if="doctor"
			class="mb-6">
			<h2 class="text-xl font-semibold">Врач: {{ doctor.full_name }}</h2>
			<p class="text-slate-600">
				Специализация: {{ doctor.specialization }}
			</p>
			<p class="text-slate-600">Кабинет: {{ doctor.cabinet_number }}</p>
		</div>

		<div class="mb-6">
			<label class="block text-sm font-medium text-slate-700 mb-2"
				>Выберите дату</label
			>
			<input
				v-model="selectedDate"
				type="date"
				:min="minDate"
				class="input-field"
				@change="loadSlots" />
		</div>

		<div
			v-if="loadingSlots"
			class="text-center py-4">
			Загрузка доступного времени...
		</div>
		<div
			v-else-if="timeSlots && timeSlots.length === 0 && selectedDate"
			class="text-center py-4 text-slate-500">
			Нет доступных слотов на эту дату
		</div>
		<div
			v-else-if="timeSlots && timeSlots.length > 0"
			class="mb-6">
			<h3 class="text-lg font-semibold mb-3">Доступное время</h3>
			<div class="grid grid-cols-2 md:grid-cols-4 gap-3">
				<button
					v-for="slot in timeSlots"
					:key="slot.id"
					@click="selectSlot(slot)"
					:class="[
						'p-2.5 rounded-xl border border-slate-300 transition text-sm font-medium',
						selectedSlot?.id === slot.id
							? 'bg-blue-700 text-white border-blue-700'
							: 'bg-white text-slate-700 hover:bg-slate-50',
					]">
					{{ formatTime(slot.start_time) }}
				</button>
			</div>
		</div>

		<div
			v-if="selectedSlot"
			class="mb-6">
			<label class="block text-sm font-medium text-slate-700 mb-2"
				>Жалобы (необязательно)</label
			>
			<textarea
				v-model="complaints"
				rows="3"
				class="input-field"
				placeholder="Опишите симптомы..."></textarea>
		</div>

		<div
			v-if="error"
			class="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700 mb-4">
			{{ error }}
		</div>

		<button
			@click="bookAppointment"
			:disabled="!selectedSlot || booking"
			class="btn-primary w-full">
			{{ booking ? "Запись..." : "Подтвердить запись" }}
		</button>
	</div>
</template>

<script setup>
	import { ref, onMounted } from "vue";
	import { useRoute, useRouter } from "vue-router";
	import { useAppointmentsStore } from "../stores/appointments";
	import { formatTime } from "../utils/date";

	const route = useRoute();
	const router = useRouter();
	const appointmentsStore = useAppointmentsStore();
	const doctorId = route.params.doctorId;
	const serviceIdFromQuery = route.query.serviceId;
	const doctor = ref(null);
	const selectedDate = ref("");
	const selectedSlot = ref(null);
	const complaints = ref("");
	const loadingSlots = ref(false);
	const booking = ref(false);
	const error = ref("");
	const timeSlots = ref([]);
	const selectedServiceId = ref(serviceIdFromQuery || null);

	const minDate = new Date().toISOString().split("T")[0];

	const loadSlots = async () => {
		if (!selectedDate.value) return;

		loadingSlots.value = true;
		selectedSlot.value = null;
		error.value = "";
		timeSlots.value = [];

		const result = await appointmentsStore.getFreeSlots(
			doctorId,
			selectedDate.value,
		);

		if (result.success) {
			timeSlots.value = result.data || [];
		} else {
			error.value = result.error;
			timeSlots.value = [];
		}
		loadingSlots.value = false;
	};

	const selectSlot = (slot) => {
		selectedSlot.value = slot;
	};

	const bookAppointment = async () => {
		if (!selectedSlot.value) return;

		booking.value = true;
		error.value = "";

		const appointmentData = {
			doctor_id: parseInt(doctorId),
			time_slot_id: selectedSlot.value.id,
			complaints: complaints.value || null,
		};

		if (selectedServiceId.value) {
			appointmentData.service_id = parseInt(selectedServiceId.value);
		}

		const result =
			await appointmentsStore.createAppointment(appointmentData);

		if (result.success) {
			router.push("/my-appointments");
		} else {
			error.value = result.error;
		}
		booking.value = false;
	};

	onMounted(async () => {
		// Загружаем список врачей если еще не загружен
		if (appointmentsStore.doctors.length === 0) {
			await appointmentsStore.getDoctors();
		}

		const doctorData = appointmentsStore.doctors.find(
			(d) => d.id == doctorId,
		);
		if (doctorData) {
			doctor.value = doctorData;
		}

		selectedDate.value = minDate;
		await loadSlots();
	});
</script>
