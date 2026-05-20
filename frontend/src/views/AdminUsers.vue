<template>
	<div class="page-card">
		<h1 class="text-2xl font-bold mb-6">Управление пользователями</h1>

		<div class="mb-4">
			<input
				v-model="searchQuery"
				type="text"
				placeholder="Поиск по имени..."
				class="input-field"
				@input="searchUsers" />
		</div>

		<div
			v-if="loading"
			class="text-center py-8">
			Загрузка...
		</div>
		<div
			v-else
			class="overflow-x-auto">
			<table class="data-table">
				<thead>
					<tr>
						<th>Имя</th>
						<th>Email</th>
						<th>Телефон</th>
						<th>Роль</th>
						<th>Действия</th>
					</tr>
				</thead>
				<tbody class="bg-white">
					<tr
						v-for="user in users"
						:key="user.id">
						<td class="px-6 py-4 whitespace-nowrap">
							{{ user.full_name }}
						</td>
						<td class="px-6 py-4 whitespace-nowrap">
							{{ user.email }}
						</td>
						<td class="px-6 py-4 whitespace-nowrap">
							{{ user.phone || "-" }}
						</td>
						<td class="px-6 py-4 whitespace-nowrap">
							<span
								:class="roleClass(user.role)"
								class="status-badge">
								{{ user.role }}
							</span>
						</td>
						<td class="px-6 py-4 whitespace-nowrap">
							<button
								@click="openRoleModal(user)"
								class="text-sm font-medium text-blue-700 hover:text-blue-900 mr-3">
								Изменить роль
							</button>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- Role Change Modal -->
		<div
			v-if="showRoleModal"
			class="fixed inset-0 z-50 h-full w-full overflow-y-auto bg-slate-900/40 backdrop-blur-sm">
			<div
				class="relative top-20 mx-auto w-96 rounded-2xl border border-slate-200 bg-white p-5 shadow-xl">
				<h3 class="text-lg font-medium mb-4">
					Изменить роль для {{ selectedUser?.full_name }}
				</h3>
				<select
					v-model="newRole"
					class="input-field mb-4">
					<option value="patient">Пациент</option>
					<option value="doctor">Врач</option>
					<option value="admin">Администратор</option>
				</select>
				<div class="flex justify-end space-x-3">
					<button
						@click="showRoleModal = false"
						class="btn-secondary">
						Отмена
					</button>
					<button
						@click="updateRole"
						class="btn-primary">
						Обновить
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
	import { ref, onMounted } from "vue";
	import api from "../services/api";

	const users = ref([]);
	const loading = ref(true);
	const searchQuery = ref("");
	const showRoleModal = ref(false);
	const selectedUser = ref(null);
	const newRole = ref("");

	const fetchUsers = async () => {
		try {
			const params = searchQuery.value
				? { full_name: searchQuery.value }
				: {};
			const response = await api.get("/admin/users", { params });
			users.value = response.data;
		} catch (error) {
			console.error("Failed to fetch users:", error);
			alert("Failed to fetch users");
		} finally {
			loading.value = false;
		}
	};

	const searchUsers = () => {
		loading.value = true;
		fetchUsers();
	};

	const openRoleModal = (user) => {
		selectedUser.value = user;
		newRole.value = user.role;
		showRoleModal.value = true;
	};

	const updateRole = async () => {
		try {
			await api.put(`/admin/users/${selectedUser.value.id}/role`, {
				role: newRole.value,
			});
			await fetchUsers();
			showRoleModal.value = false;
		} catch (error) {
			console.error("Failed to update role:", error);
			alert("Failed to update role");
		}
	};

	const makeDoctor = async (userId) => {
		const specialization = prompt("Введите специализацию:", "Терапевт");
		if (specialization) {
			const cabinetNumber = prompt("Введите номер кабинета:", "100");
			if (cabinetNumber) {
				try {
					await api.post(
						`/admin/users/${userId}/make-doctor`,
						null,
						{
							params: {
								specialization: specialization,
								cabinet_number: cabinetNumber,
							},
						},
					);
					await fetchUsers();
					alert("Пользователь успешно назначен врачом");
				} catch (error) {
					console.error("Failed to make doctor:", error);
					alert("Не удалось назначить врачом");
				}
			}
		}
	};

	const roleClass = (role) => {
		const classes = {
			patient: "bg-emerald-50 text-emerald-700",
			doctor: "bg-blue-50 text-blue-700",
			admin: "bg-violet-50 text-violet-700",
		};
		return classes[role] || "bg-slate-100 text-slate-700";
	};

	onMounted(() => {
		fetchUsers();
	});
</script>
