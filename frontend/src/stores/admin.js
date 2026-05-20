import { defineStore } from "pinia";
import { ref } from "vue";
import api from "../services/api";

export const useAdminStore = defineStore("admin", () => {
	const users = ref([]);
	const doctors = ref([]);
	const appointments = ref([]);
	const services = ref([]);
	const loading = ref(false);

	// Управление пользователями
	const getUsers = async (fullName = null) => {
		loading.value = true;
		try {
			const params = fullName ? { full_name: fullName } : {};
			const response = await api.get("/admin/users", { params });
			users.value = response.data;
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail ||
					"Ошибка загрузки пользователей",
			};
		} finally {
			loading.value = false;
		}
	};

	const changeUserRole = async (userId, role) => {
		loading.value = true;
		try {
			const response = await api.put(`/admin/users/${userId}/role`, {
				role,
			});
			await getUsers();
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error: error.response?.data?.detail || "Ошибка изменения роли",
			};
		} finally {
			loading.value = false;
		}
	};

	const makeUserDoctor = async (
		userId,
		specialization,
		cabinetNumber,
		appointmentDuration = 30,
	) => {
		loading.value = true;
		try {
			const response = await api.post(
				`/admin/users/${userId}/make-doctor`,
				null,
				{
					params: {
						specialization,
						cabinet_number: cabinetNumber,
						appointment_duration: appointmentDuration,
					},
				},
			);
			await getDoctors();
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка назначения врачом",
			};
		} finally {
			loading.value = false;
		}
	};

	// Управление врачами
	const getDoctors = async () => {
		loading.value = true;
		try {
			const response = await api.get("/admin/doctors");
			doctors.value = response.data;
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка загрузки врачей",
			};
		} finally {
			loading.value = false;
		}
	};

	const createDoctor = async (doctorData) => {
		loading.value = true;
		try {
			const response = await api.post("/admin/doctors", doctorData);
			await getDoctors();
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error: error.response?.data?.detail || "Ошибка создания врача",
			};
		} finally {
			loading.value = false;
		}
	};

	const updateDoctor = async (doctorId, doctorData) => {
		loading.value = true;
		try {
			const response = await api.put(
				`/admin/doctors/${doctorId}`,
				doctorData,
			);
			await getDoctors();
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка обновления врача",
			};
		} finally {
			loading.value = false;
		}
	};

	const deleteDoctor = async (doctorId) => {
		loading.value = true;
		try {
			await api.delete(`/admin/doctors/${doctorId}`);
			await getDoctors();
			return { success: true };
		} catch (error) {
			return {
				success: false,
				error: error.response?.data?.detail || "Ошибка удаления врача",
			};
		} finally {
			loading.value = false;
		}
	};

	const setScheduleTemplate = async (
		doctorId,
		dayOfWeek,
		startTime,
		endTime,
	) => {
		loading.value = true;
		try {
			await api.post(
				`/admin/doctors/${doctorId}/schedule/template`,
				null,
				{
					params: {
						day_of_week: dayOfWeek,
						start_time: startTime,
						end_time: endTime,
					},
				},
			);
			return { success: true };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail ||
					"Ошибка установки расписания",
			};
		} finally {
			loading.value = false;
		}
	};

	const generateSlots = async (doctorId, startDate, endDate) => {
		loading.value = true;
		try {
			await api.post(`/admin/doctors/${doctorId}/slots/generate`, null, {
				params: { start_date: startDate, end_date: endDate },
			});
			return { success: true };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка генерации слотов",
			};
		} finally {
			loading.value = false;
		}
	};

	// Управление записями
	const getAllAppointments = async (filters = {}) => {
		loading.value = true;
		try {
			const response = await api.get("/admin/appointments", {
				params: filters,
			});
			appointments.value = response.data;
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка загрузки записей",
			};
		} finally {
			loading.value = false;
		}
	};

	const confirmAppointment = async (appointmentId) => {
		loading.value = true;
		try {
			await api.put(`/admin/appointments/${appointmentId}/confirm`);
			await getAllAppointments();
			return { success: true };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail ||
					"Ошибка подтверждения записи",
			};
		} finally {
			loading.value = false;
		}
	};

	const rescheduleAppointment = async (appointmentId, newTimeSlotId) => {
		loading.value = true;
		try {
			await api.put(
				`/admin/appointments/${appointmentId}/reschedule`,
				null,
				{
					params: { new_time_slot_id: newTimeSlotId },
				},
			);
			await getAllAppointments();
			return { success: true };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка переноса записи",
			};
		} finally {
			loading.value = false;
		}
	};

	// Управление услугами
	const getServices = async () => {
		loading.value = true;
		try {
			const response = await api.get("/services/");
			services.value = response.data;
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error: error.response?.data?.detail || "Ошибка загрузки услуг",
			};
		} finally {
			loading.value = false;
		}
	};

	const createService = async (serviceData) => {
		loading.value = true;
		try {
			const response = await api.post("/services/", serviceData);
			await getServices();
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка создания услуги",
			};
		} finally {
			loading.value = false;
		}
	};

	const updateService = async (serviceId, serviceData) => {
		loading.value = true;
		try {
			const response = await api.put(
				`/services/${serviceId}`,
				serviceData,
			);
			await getServices();
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка обновления услуги",
			};
		} finally {
			loading.value = false;
		}
	};

	const deleteService = async (serviceId) => {
		loading.value = true;
		try {
			await api.delete(`/services/${serviceId}`);
			await getServices();
			return { success: true };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка удаления услуги",
			};
		} finally {
			loading.value = false;
		}
	};

	const assignServiceToDoctor = async (doctorId, serviceId) => {
		loading.value = true;
		try {
			await api.post(
				`/services/doctors/${doctorId}/services/${serviceId}`,
			);
			return { success: true };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка назначения услуги",
			};
		} finally {
			loading.value = false;
		}
	};

	const removeServiceFromDoctor = async (doctorId, serviceId) => {
		loading.value = true;
		try {
			await api.delete(
				`/services/doctors/${doctorId}/services/${serviceId}`,
			);
			return { success: true };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка удаления услуги",
			};
		} finally {
			loading.value = false;
		}
	};

	// Отчеты
	const getDoctorsLoad = async (startDate, endDate) => {
		loading.value = true;
		try {
			const response = await api.get("/admin/reports/doctors-load", {
				params: { start_date: startDate, end_date: endDate },
			});
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка загрузки отчета",
			};
		} finally {
			loading.value = false;
		}
	};

	const getDoctorServices = async (doctorId) => {
		loading.value = true;
		try {
			const response = await api.get(
				`/admin/doctors/${doctorId}/services`,
			);
			return { success: true, data: response.data };
		} catch (error) {
			return {
				success: false,
				error:
					error.response?.data?.detail ||
					"Ошибка загрузки услуг врача",
			};
		} finally {
			loading.value = false;
		}
	};

	return {
		users,
		doctors,
		appointments,
		services,
		loading,
		getUsers,
		changeUserRole,
		makeUserDoctor,
		getDoctors,
		createDoctor,
		updateDoctor,
		deleteDoctor,
		setScheduleTemplate,
		generateSlots,
		getAllAppointments,
		confirmAppointment,
		rescheduleAppointment,
		getServices,
		createService,
		updateService,
		deleteService,
		getDoctorServices,
		assignServiceToDoctor,
		removeServiceFromDoctor,
		getDoctorsLoad,
	};
});
