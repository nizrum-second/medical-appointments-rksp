<template>
	<div class="page-card">
		<div class="flex justify-between items-center mb-6">
			<h1>Управление врачами</h1>
			<button
				@click="openCreateModal"
				class="btn-primary">
				Добавить врача
			</button>
		</div>

		<div
			v-if="adminStore.loading"
			class="text-center py-8">
			Загрузка...
		</div>
		<div
			v-else-if="adminStore.doctors.length === 0"
			class="text-center py-8 text-slate-500">
			Нет врачей
		</div>
		<div
			v-else
			class="overflow-x-auto">
			<table class="data-table">
				<thead>
					<tr>
						<th>ФИО</th>
						<th>Специализация</th>
						<th>Кабинет</th>
						<th>Email</th>
						<th>Телефон</th>
						<th>Действия</th>
					</tr>
				</thead>
				<tbody class="bg-white">
					<tr
						v-for="doctor in adminStore.doctors"
						:key="doctor.id">
						<td class="px-6 py-4 whitespace-nowrap">
							{{ doctor.full_name }}
						</td>
						<td class="px-6 py-4 whitespace-nowrap">
							{{ doctor.specialization }}
						</td>
						<td class="px-6 py-4 whitespace-nowrap">
							{{ doctor.cabinet_number }}
						</td>
						<td class="px-6 py-4 whitespace-nowrap">
							{{ doctor.email }}
						</td>
						<td class="px-6 py-4 whitespace-nowrap">
							{{ doctor.phone || "-" }}
						</td>
						<td class="px-6 py-4 whitespace-nowrap">
							<div class="grid grid-cols-2 gap-2">
								<button
									@click="openServicesModal(doctor)"
									class="rounded-lg bg-violet-600 px-2 py-1.5 text-xs font-medium text-white transition hover:bg-violet-700">
									Услуги
								</button>
								<button
									@click="openScheduleModal(doctor)"
									class="rounded-lg bg-blue-700 px-2 py-1.5 text-xs font-medium text-white transition hover:bg-blue-800">
									Расписание
								</button>
								<button
									@click="openEditModal(doctor)"
									class="rounded-lg bg-emerald-600 px-2 py-1.5 text-xs font-medium text-white transition hover:bg-emerald-700">
									Редактировать
								</button>
								<button
									@click="confirmDelete(doctor)"
									class="rounded-lg bg-rose-700 px-2 py-1.5 text-xs font-medium text-white transition hover:bg-rose-800">
									Удалить
								</button>
							</div>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Модальное окно создания/редактирования врача -->
		<div
			v-if="showDoctorModal"
			class="fixed inset-0 z-50 h-full w-full overflow-y-auto bg-slate-900/40 backdrop-blur-sm">
			<div
				class="relative top-20 mx-auto w-96 rounded-2xl border border-slate-200 bg-white p-5 shadow-xl">
				<h3 class="text-lg font-medium mb-4">
					{{
						editingDoctor
							? "Редактировать врача"
							: "Добавить врача"
					}}
				</h3>

				<div class="space-y-4">
					<div>
						<label
							class="block text-sm font-medium text-gray-700 mb-2"
							>Пользователь (только с ролью "doctor")</label
						>
						<select
							v-model="doctorForm.user_id"
							class="input-field"
							:disabled="editingDoctor"
							required>
							<option value="">Выберите пользователя</option>
							<option
								v-for="user in availableDoctors"
								:key="user.id"
								:value="user.id">
								{{ user.full_name }} ({{ user.email }})
							</option>
						</select>
						<p
							v-if="
								availableDoctors.length === 0 && !editingDoctor
							"
							class="text-red-500 text-xs mt-1">
							Нет пользователей с ролью "doctor". Сначала
							назначьте пользователю роль врача.
						</p>
					</div>

					<div>
						<label
							class="block text-sm font-medium text-gray-700 mb-2"
							>Специализация</label
						>
						<input
							v-model="doctorForm.specialization"
							type="text"
							class="input-field"
							required />
					</div>

					<div>
						<label
							class="block text-sm font-medium text-gray-700 mb-2"
							>Номер кабинета</label
						>
						<input
							v-model="doctorForm.cabinet_number"
							type="text"
							class="input-field"
							required />
					</div>

					<div>
						<label
							class="block text-sm font-medium text-gray-700 mb-2"
							>Длительность приема (мин)</label
						>
						<input
							v-model="doctorForm.appointment_duration"
							type="number"
							class="input-field"
							required />
					</div>
				</div>

				<div class="flex justify-end space-x-3 mt-6">
					<button
						@click="showDoctorModal = false"
						class="btn-secondary">
						Отмена
					</button>
					<button
						@click="saveDoctor"
						:disabled="!doctorForm.user_id && !editingDoctor"
						class="btn-primary">
						Сохранить
					</button>
				</div>
			</div>
		</div>

		<!-- Модальное окно управления услугами врача -->
		<div
			v-if="showServicesModal"
			class="fixed inset-0 z-50 h-full w-full overflow-y-auto bg-slate-900/40 backdrop-blur-sm">
			<div
				class="relative top-20 mx-auto w-[800px] rounded-2xl border border-slate-200 bg-white p-5 shadow-xl">
				<div class="flex justify-between items-center mb-4">
					<h3 class="text-xl font-bold">
						Услуги врача: {{ selectedDoctor?.full_name }}
					</h3>
					<button
						@click="showServicesModal = false"
						class="text-slate-500 hover:text-slate-700 text-2xl">
						×
					</button>
				</div>

				<div class="grid md:grid-cols-2 gap-4">
					<!-- Доступные услуги -->
					<div class="rounded-xl border border-slate-200 p-3">
						<h4 class="font-semibold text-md mb-2 text-slate-700">
							📋 Доступные услуги
						</h4>
						<div class="space-y-1 max-h-96 overflow-y-auto">
							<div
								v-for="service in availableServices"
								:key="service.id"
								class="flex justify-between items-center rounded-lg border border-slate-200 p-2 hover:bg-slate-50">
								<div class="flex-1">
									<p class="font-medium text-sm">
										{{ service.name }}
									</p>
									<p class="text-xs text-slate-500">
										{{ service.duration }} мин |
										{{ service.price }} ₽
									</p>
								</div>
								<button
									@click="assignService(service.id)"
									class="rounded bg-emerald-600 px-2 py-1 text-xs text-white hover:bg-emerald-700 ml-2">
									Добавить
								</button>
							</div>
							<div
								v-if="availableServices.length === 0"
								class="text-center text-slate-500 py-4 text-sm">
								Нет доступных услуг
							</div>
						</div>
					</div>

					<!-- Назначенные услуги -->
					<div class="rounded-xl border border-slate-200 p-3">
						<h4 class="font-semibold text-md mb-2 text-slate-700">
							✅ Назначенные услуги
						</h4>
						<div class="space-y-1 max-h-96 overflow-y-auto">
							<div
								v-for="service in doctorServices"
								:key="service.id"
								class="flex justify-between items-center rounded-lg border border-slate-200 p-2 hover:bg-slate-50">
								<div class="flex-1">
									<p class="font-medium text-sm">
										{{ service.name }}
									</p>
									<p class="text-xs text-slate-500">
										{{ service.duration }} мин |
										{{ service.price }} ₽
									</p>
								</div>
								<button
									@click="removeService(service.id)"
									class="rounded bg-rose-700 px-2 py-1 text-xs text-white hover:bg-rose-800 ml-2">
									Удалить
								</button>
							</div>
							<div
								v-if="doctorServices.length === 0"
								class="text-center text-slate-500 py-4 text-sm">
								Нет назначенных услуг
							</div>
						</div>
					</div>
				</div>

				<div class="flex justify-end mt-4">
					<button
						@click="showServicesModal = false"
						class="btn-secondary">
						Закрыть
					</button>
				</div>
			</div>
		</div>

		<!-- Модальное окно настройки расписания -->
		<div
			v-if="showScheduleModal"
			class="fixed inset-0 z-50 h-full w-full overflow-y-auto bg-slate-900/40 backdrop-blur-sm">
			<div
				class="relative top-20 mx-auto w-[500px] rounded-2xl border border-slate-200 bg-white p-5 shadow-xl">
				<h3 class="text-lg font-medium mb-4">
					Настройка расписания для {{ selectedDoctor?.full_name }}
				</h3>

				<div class="mb-6 rounded-xl border border-slate-200 bg-slate-50 p-4">
					<h4 class="font-semibold text-md mb-3 text-slate-700">
						📅 Установить шаблон расписания
					</h4>
					<div class="space-y-3">
						<div>
							<label
								class="block text-sm font-medium text-gray-700 mb-2"
								>День недели</label
							>
							<select
								v-model="scheduleForm.day_of_week"
								class="input-field">
								<option value="0">Понедельник</option>
								<option value="1">Вторник</option>
								<option value="2">Среда</option>
								<option value="3">Четверг</option>
								<option value="4">Пятница</option>
								<option value="5">Суббота</option>
								<option value="6">Воскресенье</option>
							</select>
						</div>

						<div class="grid grid-cols-2 gap-3">
							<div>
								<label
									class="block text-sm font-medium text-gray-700 mb-2"
									>Время начала</label
								>
								<input
									v-model="scheduleForm.start_time"
									type="time"
									class="input-field"
									required />
							</div>
							<div>
								<label
									class="block text-sm font-medium text-gray-700 mb-2"
									>Время окончания</label
								>
								<input
									v-model="scheduleForm.end_time"
									type="time"
									class="input-field"
									required />
							</div>
						</div>

						<button
							@click="saveScheduleTemplate"
							class="btn-primary w-full">
							Сохранить шаблон
						</button>
					</div>
				</div>

				<div class="mb-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
					<h4 class="font-semibold text-md mb-3 text-slate-700">
						⚙️ Генерация слотов
					</h4>
					<div class="space-y-3">
						<div>
							<label
								class="block text-sm font-medium text-gray-700 mb-2"
								>Дата начала</label
							>
							<input
								v-model="slotGeneration.start_date"
								type="date"
								class="input-field" />
						</div>
						<div>
							<label
								class="block text-sm font-medium text-gray-700 mb-2"
								>Дата окончания</label
							>
							<input
								v-model="slotGeneration.end_date"
								type="date"
								class="input-field" />
						</div>
						<button
							@click="generateSlots"
							class="btn-primary w-full">
							Сгенерировать слоты
						</button>
					</div>
				</div>

				<div class="flex justify-end">
					<button
						@click="showScheduleModal = false"
						class="btn-secondary">
						Закрыть
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
	import { ref, computed, onMounted } from "vue";
	import { useAdminStore } from "../stores/admin";

	const adminStore = useAdminStore();
	const showDoctorModal = ref(false);
	const showScheduleModal = ref(false);
	const showServicesModal = ref(false);
	const editingDoctor = ref(null);
	const selectedDoctor = ref(null);
	const doctorServices = ref([]);
	const allServices = ref([]);

	const doctorForm = ref({
		user_id: "",
		specialization: "",
		cabinet_number: "",
		appointment_duration: 30,
	});

	const scheduleForm = ref({
		day_of_week: 0,
		start_time: "09:00",
		end_time: "17:00",
	});

	const slotGeneration = ref({
		start_date: "",
		end_date: "",
	});

	const availableDoctors = computed(() => {
		return adminStore.users.filter((user) => user.role === "doctor");
	});

	const availableServices = computed(() => {
		return allServices.value.filter(
			(service) =>
				!doctorServices.value.some((ds) => ds.id === service.id),
		);
	});

	const openCreateModal = () => {
		editingDoctor.value = null;
		doctorForm.value = {
			user_id: "",
			specialization: "",
			cabinet_number: "",
			appointment_duration: 30,
		};
		showDoctorModal.value = true;
	};

	const openEditModal = (doctor) => {
		editingDoctor.value = doctor;
		doctorForm.value = {
			user_id: doctor.user_id,
			specialization: doctor.specialization,
			cabinet_number: doctor.cabinet_number,
			appointment_duration: doctor.appointment_duration,
		};
		showDoctorModal.value = true;
	};

	const saveDoctor = async () => {
		if (!doctorForm.value.user_id && !editingDoctor.value) {
			alert('Выберите пользователя с ролью "doctor"');
			return;
		}

		let result;

		if (editingDoctor.value) {
			result = await adminStore.updateDoctor(
				editingDoctor.value.id,
				doctorForm.value,
			);
		} else {
			result = await adminStore.createDoctor(doctorForm.value);
		}

		if (result.success) {
			showDoctorModal.value = false;
			alert(editingDoctor.value ? "Врач обновлен" : "Врач создан");
		} else {
			alert(result.error);
		}
	};

	const openServicesModal = async (doctor) => {
		selectedDoctor.value = doctor;
		showServicesModal.value = true;

		const servicesResult = await adminStore.getServices();
		if (servicesResult.success) {
			allServices.value = servicesResult.data;
		}

		const doctorServicesResult = await adminStore.getDoctorServices(
			doctor.id,
		);
		if (doctorServicesResult.success) {
			doctorServices.value = doctorServicesResult.data;
		} else {
			doctorServices.value = [];
		}
	};

	const assignService = async (serviceId) => {
		const result = await adminStore.assignServiceToDoctor(
			selectedDoctor.value.id,
			serviceId,
		);
		if (result.success) {
			const service = allServices.value.find((s) => s.id === serviceId);
			if (service) {
				doctorServices.value.push(service);
			}
			alert("Услуга добавлена");
		} else {
			alert(result.error);
		}
	};

	const removeService = async (serviceId) => {
		if (confirm("Удалить услугу у врача?")) {
			const result = await adminStore.removeServiceFromDoctor(
				selectedDoctor.value.id,
				serviceId,
			);
			if (result.success) {
				doctorServices.value = doctorServices.value.filter(
					(s) => s.id !== serviceId,
				);
				alert("Услуга удалена");
			} else {
				alert(result.error);
			}
		}
	};

	const openScheduleModal = (doctor) => {
		selectedDoctor.value = doctor;
		scheduleForm.value = {
			day_of_week: 0,
			start_time: "09:00",
			end_time: "17:00",
		};
		slotGeneration.value = {
			start_date: "",
			end_date: "",
		};
		showScheduleModal.value = true;
	};

	const saveScheduleTemplate = async () => {
		const result = await adminStore.setScheduleTemplate(
			selectedDoctor.value.id,
			scheduleForm.value.day_of_week,
			scheduleForm.value.start_time,
			scheduleForm.value.end_time,
		);

		if (result.success) {
			alert("Шаблон расписания сохранен");
		} else {
			alert(result.error);
		}
	};

	const generateSlots = async () => {
		if (
			!slotGeneration.value.start_date ||
			!slotGeneration.value.end_date
		) {
			alert("Выберите даты начала и окончания");
			return;
		}

		const result = await adminStore.generateSlots(
			selectedDoctor.value.id,
			slotGeneration.value.start_date,
			slotGeneration.value.end_date,
		);

		if (result.success) {
			alert("Слоты успешно сгенерированы");
		} else {
			alert(result.error);
		}
	};

	const confirmDelete = async (doctor) => {
		if (confirm(`Удалить врача ${doctor.full_name}?`)) {
			const result = await adminStore.deleteDoctor(doctor.id);
			if (result.success) {
				alert("Врач удален");
			} else {
				alert(result.error);
			}
		}
	};

	onMounted(async () => {
		await Promise.all([
			adminStore.getDoctors(),
			adminStore.getUsers(),
			adminStore.getServices(),
		]);
	});
</script>
