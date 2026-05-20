<template>
	<div class="space-y-6">
		<div class="page-card">
			<h1 class="mb-4">Наши врачи</h1>

			<div class="mb-4 grid md:grid-cols-2 gap-4">
				<div>
					<input
						v-model="specializationFilter"
						type="text"
						placeholder="Фильтр по специализации..."
						class="input-field"
						@input="filterDoctors" />
				</div>
				<div>
					<select
						v-model="serviceFilter"
						class="input-field"
						@change="filterDoctorsByService">
						<option value="">Все услуги</option>
						<option
							v-for="service in services"
							:key="service.id"
							:value="service.id">
							{{ service.name }}
						</option>
					</select>
				</div>
			</div>

			<div
				v-if="loading"
				class="text-center py-8">
				Загрузка...
			</div>
			<div
				v-else-if="filteredDoctors.length === 0"
				class="text-center py-8 text-slate-500">
				Врачи не найдены
			</div>
			<div
				v-else
				class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
				<div
					v-for="doctor in filteredDoctors"
					:key="doctor.id"
					class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow">
					<h3 class="text-lg font-semibold">
						{{ doctor.full_name }}
					</h3>
					<p class="text-slate-600">
						Специализация: {{ doctor.specialization }}
					</p>
					<p class="text-slate-600">
						Кабинет: {{ doctor.cabinet_number }}
					</p>
					<router-link
						:to="`/book-appointment/${doctor.id}`"
						class="btn-primary inline-block mt-3 text-center w-full">
						Записаться на прием
					</router-link>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
	import { ref, onMounted } from "vue";
	import { useAppointmentsStore } from "../stores/appointments";
	import api from "../services/api";

	const appointmentsStore = useAppointmentsStore();
	const loading = ref(true);
	const specializationFilter = ref("");
	const serviceFilter = ref("");
	const services = ref([]);
	const allDoctors = ref([]);

	const filteredDoctors = ref([]);

	const loadServices = async () => {
		try {
			const response = await api.get("/services/");
			services.value = response.data || [];
		} catch (error) {
			console.error("Failed to load services:", error);
		}
	};

	const filterDoctorsByService = async () => {
		if (!serviceFilter.value) {
			filteredDoctors.value = allDoctors.value;
			return;
		}

		try {
			const response = await api.get(
				`/patients/services/${serviceFilter.value}/doctors`,
			);
			filteredDoctors.value = response.data || [];
		} catch (error) {
			console.error("Failed to filter doctors by service:", error);
			filteredDoctors.value = [];
		}
	};

	const filterDoctors = () => {
		if (!specializationFilter.value) {
			filteredDoctors.value = allDoctors.value;
		} else {
			filteredDoctors.value = allDoctors.value.filter((doctor) =>
				doctor.specialization
					.toLowerCase()
					.includes(specializationFilter.value.toLowerCase()),
			);
		}
	};

	onMounted(async () => {
		await Promise.all([appointmentsStore.getDoctors(), loadServices()]);
		allDoctors.value = appointmentsStore.doctors;
		filteredDoctors.value = allDoctors.value;
		loading.value = false;
	});
</script>
