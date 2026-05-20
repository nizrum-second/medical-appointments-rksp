<template>
	<div class="space-y-6">
		<div class="page-card">
			<h1 class="mb-2">Докторская панель</h1>
			<p class="text-slate-600">
				Добро пожаловать, {{ authStore.user?.full_name }}
			</p>
			<p class="text-slate-600">
				Специализация: {{ doctorInfo?.specialization }}
			</p>
			<p class="text-slate-600">
				Кабинет: {{ doctorInfo?.cabinet_number }}
			</p>
		</div>

		<div class="page-card">
			<h2 class="text-xl font-semibold mb-4">Сегодняшние записи</h2>
			<div
				v-if="loadingToday"
				class="text-center py-8">
				Загрузка...
			</div>
			<div
				v-else-if="todayAppointments.length === 0"
				class="text-slate-500 text-center py-8">
				Нет записей на сегодня
			</div>
			<div
				v-else
				class="space-y-4">
				<div
					v-for="item in todayAppointments"
					:key="item.slot_id"
					class="rounded-xl border border-slate-200 p-4 shadow-sm">
					<div class="flex justify-between items-start">
						<div class="flex-1">
							<p class="font-semibold text-lg">
								{{ formatTime(item.start_time) }} -
								{{ formatTime(item.end_time) }}
							</p>
							<p class="text-sm mt-1">
								<span
									:class="getStatusClass(item.status)"
								class="status-badge">
									{{ getStatusText(item.status) }}
								</span>
							</p>
							<div
								v-if="item.status === 'booked' && item.patient"
								class="mt-3 rounded-lg bg-blue-50 p-3">
								<p class="font-semibold text-slate-800">
									Пациент:
									{{
										item.patient.patient_name ||
										item.patient.full_name ||
										"Не указан"
									}}
								</p>
								<p
									v-if="
										item.patient.patient_phone ||
										item.patient.phone
									"
									class="text-sm text-slate-600 mt-1">
									Телефон:
									{{
										item.patient.patient_phone ||
										item.patient.phone
									}}
								</p>
								<p
									v-if="item.complaints"
									class="text-sm text-slate-600 mt-1">
									Жалобы: {{ item.complaints }}
								</p>
							</div>
						</div>
						<div class="flex space-x-2">
							<button
								v-if="item.status === 'booked'"
								@click="
									completeAppointment(item.appointment_id)
								"
								:disabled="completing"
								class="btn-primary text-sm px-3 py-1">
								{{
									completing ? "Завершение..." : "Завершить"
								}}
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
	import { ref, computed, onMounted } from "vue";
	import { useAuthStore } from "../stores/auth";
	import api from "../services/api";

	const authStore = useAuthStore();
	const doctorInfo = ref(null);
	const todaySchedule = ref([]);
	const loadingToday = ref(true);
	const completing = ref(false);

	const formatTime = (datetime) => {
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

	const getStatusText = (status) => {
		return status === "booked" ? "Есть запись" : "Свободно";
	};

	const getStatusClass = (status) => {
		return status === "booked"
		? "bg-blue-50 text-blue-700"
		: "bg-emerald-50 text-emerald-700";
	};

	const todayAppointments = computed(() => {
		return todaySchedule.value.filter((item) => item.status === "booked");
	});

	const completeAppointment = async (appointmentId) => {
		if (!appointmentId) {
			alert("ID записи не найден");
			return;
		}

		if (confirm("Завершить прием?")) {
			completing.value = true;
			try {
				await api.put(
					`/doctors/appointments/${appointmentId}/complete`,
				);
				alert("Прием успешно завершен");
				await loadTodaySchedule();
			} catch (error) {
				console.error("Failed to complete appointment:", error);
				alert(
					error.response?.data?.detail ||
						"Ошибка при завершении приема",
				);
			} finally {
				completing.value = false;
			}
		}
	};

	const loadDoctorInfo = async () => {
		try {
			const response = await api.get("/doctors/profile");
			doctorInfo.value = response.data;
		} catch (error) {
			console.error("Failed to load doctor info:", error);
		}
	};

	const loadTodaySchedule = async () => {
		const today = new Date();
		const year = today.getFullYear();
		const month = String(today.getMonth() + 1).padStart(2, "0");
		const day = String(today.getDate()).padStart(2, "0");
		const todayDate = `${year}-${month}-${day}`;

		loadingToday.value = true;
		try {
			const response = await api.get("/doctors/schedule", {
				params: { target_date: todayDate },
			});

			if (Array.isArray(response.data)) {
				todaySchedule.value = response.data;
			} else {
				todaySchedule.value = [];
			}
		} catch (error) {
			console.error("Failed to load today schedule:", error);
			todaySchedule.value = [];
		} finally {
			loadingToday.value = false;
		}
	};

	onMounted(async () => {
		await Promise.all([loadDoctorInfo(), loadTodaySchedule()]);
	});
</script>
