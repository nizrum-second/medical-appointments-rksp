<template>
	<div class="page-card">
		<h1 class="mb-6">Медицинские услуги</h1>

		<div
			v-if="loading"
			class="text-center py-8">
			Загрузка...
		</div>
		<div
			v-else-if="services.length === 0"
			class="text-center py-8 text-slate-500">
			Нет доступных услуг
		</div>
		<div
			v-else
			class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
			<div
				v-for="service in services"
				:key="service.id"
				@click="selectService(service)"
				class="cursor-pointer rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:shadow hover:border-blue-300">
				<h3 class="text-lg font-semibold text-blue-700">
					{{ service.name }}
				</h3>
				<p
					v-if="service.description"
					class="text-slate-600 text-sm mt-2">
					{{ service.description }}
				</p>
				<div class="mt-3 flex justify-between items-center">
					<p
						v-if="service.price"
						class="text-slate-800 font-semibold">
						{{ service.price }} ₽
					</p>
					<p class="text-slate-500 text-sm">
						Длительность: {{ service.duration }} мин
					</p>
				</div>
				<button class="btn-primary w-full mt-3 text-sm">
					Записаться
				</button>
			</div>
		</div>

		<!-- Модальное окно с врачами -->
		<div
			v-if="showDoctorsModal"
			class="fixed inset-0 z-50 h-full w-full overflow-y-auto bg-slate-900/40 backdrop-blur-sm">
			<div
				class="relative top-20 mx-auto w-[600px] rounded-2xl border border-slate-200 bg-white p-6 shadow-xl">
				<div class="flex justify-between items-center mb-4">
					<h3 class="text-xl font-bold">
						Врачи для услуги: {{ selectedService?.name }}
					</h3>
					<button
						@click="showDoctorsModal = false"
						class="text-slate-500 hover:text-slate-700 text-2xl">
						×
					</button>
				</div>

				<div
					v-if="loadingDoctors"
					class="text-center py-8">
					Загрузка врачей...
				</div>
				<div
					v-else-if="doctors.length === 0"
					class="text-center py-8 text-slate-500">
					Нет врачей, предоставляющих эту услугу
				</div>
				<div
					v-else
					class="space-y-3 max-h-96 overflow-y-auto">
					<div
						v-for="doctor in doctors"
						:key="doctor.id"
						class="rounded-xl border border-slate-200 p-4 transition hover:shadow-sm">
						<div class="flex justify-between items-start">
							<div>
								<p class="font-semibold text-lg">
									{{ doctor.full_name || "Врач" }}
								</p>
								<p class="text-slate-600">
									Специализация: {{ doctor.specialization }}
								</p>
								<p class="text-slate-600">
									Кабинет: {{ doctor.cabinet_number }}
								</p>
								<p class="text-slate-600 text-sm">
									Длительность приема:
									{{ doctor.appointment_duration }} мин
								</p>
							</div>
							<button
								@click="bookWithDoctor(doctor)"
								class="btn-primary text-sm px-4 py-2">
								Записаться
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
	import { ref, onMounted } from "vue";
	import { useRouter } from "vue-router";
	import api from "../services/api";

	const router = useRouter();
	const services = ref([]);
	const doctors = ref([]);
	const loading = ref(false);
	const loadingDoctors = ref(false);
	const showDoctorsModal = ref(false);
	const selectedService = ref(null);

	const loadServices = async () => {
		loading.value = true;
		try {
			const response = await api.get("/services/");
			services.value = response.data || [];
		} catch (error) {
			console.error("Failed to load services:", error);
			alert("Ошибка загрузки услуг");
			services.value = [];
		} finally {
			loading.value = false;
		}
	};

	const selectService = async (service) => {
		selectedService.value = service;
		showDoctorsModal.value = true;
		loadingDoctors.value = true;

		try {
			const response = await api.get(
				`/patients/services/${service.id}/doctors`,
			);
			doctors.value = response.data || [];
		} catch (error) {
			console.error("Failed to load doctors for service:", error);
			alert("Ошибка загрузки врачей");
			doctors.value = [];
		} finally {
			loadingDoctors.value = false;
		}
	};

	const bookWithDoctor = (doctor) => {
		showDoctorsModal.value = false;
		router.push(
			`/book-appointment/${doctor.id}?serviceId=${selectedService.value.id}`,
		);
	};

	onMounted(() => {
		loadServices();
	});
</script>
