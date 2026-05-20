<template>
	<div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow">
		<div class="flex justify-between items-start">
			<div class="flex-1">
				<h3 class="font-semibold">
					{{
						isDoctor
							? appointment.patient_name || "Пациент"
							: appointment.doctor_name || "Врач"
					}}
				</h3>
				<p
					v-if="!isDoctor && appointment.doctor_specialization"
					class="text-sm text-slate-500">
					{{ appointment.doctor_specialization }}
				</p>
				<p
					v-if="appointment.doctor_cabinet"
					class="text-sm text-slate-500">
					Кабинет: {{ appointment.doctor_cabinet }}
				</p>
				<p class="text-sm text-slate-500">
					Дата: {{ formatDate(appointment.time_start) }}
				</p>
				<p class="text-sm text-slate-500">
					Время: {{ formatTime(appointment.time_start) }} -
					{{ formatTime(appointment.time_end) }}
				</p>
				<p
					v-if="appointment.service_name"
					class="text-sm text-slate-500">
					Услуга: {{ appointment.service_name }}
				</p>
				<p
					v-if="appointment.complaints"
					class="text-sm text-slate-500">
					Жалобы: {{ appointment.complaints }}
				</p>
				<p
					v-if="appointment.patient_phone"
					class="text-sm text-slate-500">
					Телефон: {{ appointment.patient_phone }}
				</p>
				<p class="text-sm mt-2 text-slate-600">
					Статус:
					<span
						:class="statusClass"
						class="ml-2 status-badge">
						{{ statusText }}
					</span>
				</p>
			</div>
			<div class="flex space-x-2">
				<button
					v-if="
						showCancel &&
						(appointment.status === 'scheduled' ||
							appointment.status === 'confirmed')
					"
					@click="$emit('cancel')"
					class="btn-danger text-sm px-3 py-1">
					Отменить
				</button>
				<button
					v-if="showComplete && appointment.status === 'confirmed'"
					@click="$emit('complete')"
					class="btn-primary text-sm px-3 py-1">
					Завершить
				</button>
			</div>
		</div>
	</div>
</template>

<script setup>
	import { computed } from "vue";
	import { formatDate, formatTime } from "../utils/date";

	const props = defineProps({
		appointment: {
			type: Object,
			required: true,
		},
		showCancel: {
			type: Boolean,
			default: false,
		},
		showComplete: {
			type: Boolean,
			default: false,
		},
		isDoctor: {
			type: Boolean,
			default: false,
		},
	});

	defineEmits(["cancel", "complete"]);

	const statusText = computed(() => {
		const statuses = {
			scheduled: "Запланирована",
			confirmed: "Подтверждена",
			completed: "Завершена",
			cancelled: "Отменена",
			available: "Свободно",
		};
		return (
			statuses[props.appointment.status] ||
			props.appointment.status ||
			"Неизвестно"
		);
	});

	const statusClass = computed(() => {
		const classes = {
		scheduled: "bg-blue-50 text-blue-700",
		confirmed: "bg-emerald-50 text-emerald-700",
		completed: "bg-slate-100 text-slate-700",
		cancelled: "bg-rose-50 text-rose-700",
		available: "bg-slate-100 text-slate-600",
		};
	return classes[props.appointment.status] || "bg-slate-100 text-slate-700";
	});
</script>
