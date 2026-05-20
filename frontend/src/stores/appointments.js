import { defineStore } from "pinia";
import { ref } from "vue";
import api from "../services/api";

export const useAppointmentsStore = defineStore("appointments", () => {
	const appointments = ref([]);
	const doctors = ref([]);
	const timeSlots = ref([]);

	const getDoctors = async (specialization = null) => {
		try {
			const params = specialization ? { specialization } : {};
			const response = await api.get("/patients/doctors", { params });
			doctors.value = response.data || [];
			return { success: true, data: doctors.value };
		} catch (error) {
			console.error("getDoctors error:", error);
			doctors.value = [];
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка загрузки врачей",
			};
		}
	};

	const getFreeSlots = async (doctorId, date) => {
		try {
			const response = await api.get(
				`/patients/doctors/${doctorId}/slots`,
				{
					params: { date },
				},
			);
			timeSlots.value = response.data || [];
			return { success: true, data: timeSlots.value };
		} catch (error) {
			console.error("getFreeSlots error:", error);
			timeSlots.value = [];
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка загрузки слотов",
			};
		}
	};

	const createAppointment = async (appointmentData) => {
		try {
			const response = await api.post(
				"/patients/appointments",
				appointmentData,
			);
			await getMyAppointments();
			return { success: true, data: response.data };
		} catch (error) {
			console.error("createAppointment error:", error);
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка создания записи",
			};
		}
	};

	const getMyAppointments = async () => {
		try {
			const response = await api.get("/patients/appointments");
			appointments.value = response.data || [];
			return { success: true, data: appointments.value };
		} catch (error) {
			console.error("getMyAppointments error:", error);
			appointments.value = [];
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка загрузки записей",
			};
		}
	};

	const cancelAppointment = async (appointmentId) => {
		try {
			await api.delete(`/patients/appointments/${appointmentId}`);
			await getMyAppointments();
			return { success: true };
		} catch (error) {
			console.error("cancelAppointment error:", error);
			return {
				success: false,
				error: error.response?.data?.detail || "Ошибка отмены записи",
			};
		}
	};

	const rebookAppointment = async (appointmentId, newTimeSlotId) => {
		try {
			await api.post(
				`/patients/appointments/${appointmentId}/rebook`,
				null,
				{
					params: { new_time_slot_id: newTimeSlotId },
				},
			);
			await getMyAppointments();
			return { success: true };
		} catch (error) {
			console.error("rebookAppointment error:", error);
			return {
				success: false,
				error:
					error.response?.data?.detail || "Ошибка переноса записи",
			};
		}
	};

	return {
		appointments,
		doctors,
		timeSlots,
		getDoctors,
		getFreeSlots,
		createAppointment,
		getMyAppointments,
		cancelAppointment,
		rebookAppointment,
	};
});
