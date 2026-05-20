<template>
	<div class="page-card">
		<h1 class="mb-6">Управление записями</h1>

		<!-- Фильтры -->
		<div class="grid md:grid-cols-4 gap-4 mb-6">
			<div>
				<label class="block text-sm font-medium text-slate-700 mb-2"
					>Врач</label
				>
				<select
					v-model="filters.doctor_id"
					class="input-field"
					@change="applyFilters">
					<option value="">Все врачи</option>
					<option
						v-for="doctor in adminStore.doctors"
						:key="doctor.id"
						:value="doctor.id">
						{{ doctor.full_name }}
					</option>
				</select>
			</div>

			<div>
				<label class="block text-sm font-medium text-slate-700 mb-2"
					>Статус</label
				>
				<select
					v-model="filters.status"
					class="input-field"
					@change="applyFilters">
					<option value="">Все статусы</option>
					<option value="scheduled">Запланирована</option>
					<option value="confirmed">Подтверждена</option>
					<option value="completed">Завершена</option>
					<option value="cancelled">Отменена</option>
				</select>
			</div>

			<div>
				<label class="block text-sm font-medium text-slate-700 mb-2"
					>Дата от</label
				>
				<input
					v-model="filters.start_date"
					type="date"
					class="input-field"
					@change="applyFilters" />
			</div>

			<div>
				<label class="block text-sm font-medium text-slate-700 mb-2"
					>Дата до</label
				>
				<input
					v-model="filters.end_date"
					type="date"
					class="input-field"
					@change="applyFilters" />
			</div>
		</div>

		<div
			v-if="adminStore.loading"
			class="text-center py-8">
			Загрузка...
		</div>
		<div
			v-else-if="adminStore.appointments.length === 0"
			class="text-center py-8 text-slate-500">
			Нет записей
		</div>
		<div
			v-else
			class="overflow-x-auto">
			<table class="data-table">
				<thead>
					<tr>
						<th>Пациент</th>
						<th>Врач</th>
						<th>Дата</th>
						<th>Время</th>
						<th>Услуга</th>
						<th>Статус</th>
						<th>Действия</th>
					</tr>
				</thead>
				<tbody class="bg-white">
					<tr
						v-for="appointment in adminStore.appointments"
						:key="appointment.id">
						<td class="px-6 py-4">
							<div class="font-medium">
								{{ appointment.patient_name || "—" }}
							</div>
							<div class="text-sm text-slate-500">
								{{ appointment.patient_phone || "—" }}
							</div>
						</td>
						<td class="px-6 py-4">
							<div>{{ appointment.doctor_name || "—" }}</div>
							<div class="text-sm text-slate-500">
								{{ appointment.doctor_specialization || "—" }}
							</div>
						</td>
						<td class="px-6 py-4">
							{{ formatDate(appointment.time_start) }}
						</td>
						<td class="px-6 py-4">
							{{ formatTime(appointment.time_start) }} -
							{{ formatTime(appointment.time_end) }}
						</td>
						<td class="px-6 py-4">
							{{ appointment.service_name || "—" }}
						</td>
						<td class="px-6 py-4">
							<span
								:class="statusClass(appointment.status)"
								class="status-badge">
								{{ statusText(appointment.status) }}
							</span>
						</td>
						<td class="px-6 py-4 whitespace-nowrap">
							<button
								v-if="appointment.status === 'scheduled'"
								@click="confirmAppointment(appointment.id)"
								class="btn-primary mr-2 text-sm px-3 py-1">
								Подтвердить
							</button>
							<button
								@click="openRescheduleModal(appointment)"
								class="btn-secondary text-sm px-3 py-1">
								Перенести
							</button>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Модальное окно переноса записи -->
		<div
			v-if="showRescheduleModal"
			class="fixed inset-0 z-50 h-full w-full overflow-y-auto bg-slate-900/40 backdrop-blur-sm">
			<div
				class="relative top-20 mx-auto w-96 rounded-2xl border border-slate-200 bg-white p-5 shadow-xl">
				<h3 class="text-lg font-medium mb-4">Перенос записи</h3>
				<p class="mb-2">
					Пациент: {{ selectedAppointment?.patient_name }}
				</p>
				<p class="mb-4">
					Врач: {{ selectedAppointment?.doctor_name }}
				</p>

				<div class="mb-4">
					<label class="block text-sm font-medium text-slate-700 mb-2"
						>Новая дата</label
					>
					<input
						v-model="newDate"
						type="date"
						class="input-field"
						@change="loadSlotsForReschedule" />
				</div>

				<div
					v-if="availableSlots.length > 0"
					class="mb-4">
					<label class="block text-sm font-medium text-slate-700 mb-2"
						>Новое время</label
					>
					<select
						v-model="selectedSlotId"
						class="input-field">
						<option value="">Выберите время</option>
						<option
							v-for="slot in availableSlots"
							:key="slot.id"
							:value="slot.id">
							{{ formatTime(slot.time_start) }}
						</option>
					</select>
				</div>

				<div
					v-else-if="newDate"
					class="text-center text-slate-500 mb-4">
					Нет доступных слотов на эту дату
				</div>

				<div class="flex justify-end space-x-3">
					<button
						@click="showRescheduleModal = false"
						class="btn-secondary">
						Отмена
					</button>
					<button
						@click="rescheduleAppointment"
						:disabled="!selectedSlotId"
						class="btn-primary">
						Перенести
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
	import { ref, onMounted } from "vue";
	import { useAdminStore } from "../stores/admin";
	import { formatDate, formatTime } from "../utils/date";
	import api from "../services/api";

	const adminStore = useAdminStore();
	const filters = ref({
		doctor_id: "",
		status: "",
		start_date: "",
		end_date: "",
	});
	const showRescheduleModal = ref(false);
	const selectedAppointment = ref(null);
	const newDate = ref("");
	const selectedSlotId = ref("");
	const availableSlots = ref([]);

	const statusText = (status) => {
		const statuses = {
			scheduled: "Запланирована",
			confirmed: "Подтверждена",
			completed: "Завершена",
			cancelled: "Отменена",
		};
		return statuses[status] || status;
	};

	const statusClass = (status) => {
		const classes = {
		scheduled: "bg-amber-50 text-amber-700",
		confirmed: "bg-emerald-50 text-emerald-700",
		completed: "bg-blue-50 text-blue-700",
		cancelled: "bg-rose-50 text-rose-700",
		};
	return classes[status] || "bg-slate-100 text-slate-700";
	};

	const applyFilters = () => {
		adminStore.getAllAppointments(filters.value);
	};

	const confirmAppointment = async (appointmentId) => {
		if (confirm("Подтвердить запись?")) {
			const result = await adminStore.confirmAppointment(appointmentId);
			if (result.success) {
				alert("Запись подтверждена");
				await applyFilters();
			} else {
				alert(result.error);
			}
		}
	};

	const openRescheduleModal = (appointment) => {
		selectedAppointment.value = appointment;
		newDate.value = "";
		selectedSlotId.value = "";
		availableSlots.value = [];
		showRescheduleModal.value = true;
	};

	const loadSlotsForReschedule = async () => {
		if (!newDate.value || !selectedAppointment.value) return;

		try {
			const response = await api.get(
				`/patients/doctors/${selectedAppointment.value.doctor_id}/slots`,
				{
					params: { date: newDate.value },
				},
			);
			availableSlots.value = response.data || [];
		} catch (error) {
			console.error("Failed to load slots:", error);
			availableSlots.value = [];
		}
	};

	const rescheduleAppointment = async () => {
		if (!selectedSlotId.value) {
			alert("Выберите новое время");
			return;
		}

		const result = await adminStore.rescheduleAppointment(
			selectedAppointment.value.id,
			selectedSlotId.value,
		);

		if (result.success) {
			showRescheduleModal.value = false;
			alert("Запись перенесена");
			await applyFilters();
		} else {
			alert(result.error);
		}
	};

	onMounted(async () => {
		await Promise.all([
			adminStore.getAllAppointments(),
			adminStore.getDoctors(),
		]);
	});
</script>
