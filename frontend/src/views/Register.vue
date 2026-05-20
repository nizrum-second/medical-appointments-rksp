<template>
	<div class="min-h-screen flex items-center justify-center px-4 py-10">
		<div class="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
			<div class="mb-8 text-center">
				<h2 class="text-3xl font-semibold tracking-tight text-slate-900">
					Регистрация пациента
				</h2>
				<p class="mt-2 text-sm text-slate-500">
					Создание учетной записи для онлайн-записи
				</p>
			</div>
			<form
				class="space-y-5"
				@submit.prevent="handleRegister">
				<div class="space-y-4">
					<div>
						<input
							v-model="fullName"
							type="text"
							required
							class="input-field"
							placeholder="Полное имя" />
					</div>
					<div>
						<input
							v-model="email"
							type="email"
							required
							class="input-field"
							placeholder="Адрес электронной почты" />
					</div>
					<div>
						<input
							v-model="phone"
							type="tel"
							class="input-field"
							placeholder="Телефон (необязательно)" />
					</div>
					<div>
						<input
							v-model="password"
							type="password"
							required
							class="input-field"
							placeholder="Пароль" />
					</div>
				</div>

				<div
					v-if="error"
					class="rounded-lg bg-rose-50 px-3 py-2 text-center text-sm text-rose-700">
					{{ error }}
				</div>

				<div>
					<button
						type="submit"
						class="btn-primary w-full">
						Зарегистрироваться
					</button>
				</div>

				<div class="text-center">
					<router-link
						to="/login"
						class="text-sm font-medium text-blue-700 hover:text-blue-800">
						Уже есть аккаунт? Войти
					</router-link>
				</div>
			</form>
		</div>
	</div>
</template>

<script setup>
	import { ref } from "vue";
	import { useAuthStore } from "../stores/auth";
	import { useRouter } from "vue-router";

	const authStore = useAuthStore();
	const router = useRouter();
	const fullName = ref("");
	const email = ref("");
	const phone = ref("");
	const password = ref("");
	const error = ref("");

	const handleRegister = async () => {
		const result = await authStore.register({
			full_name: fullName.value,
			email: email.value,
			phone: phone.value || null,
			role: "patient",
			password: password.value,
		});

		if (result.success) {
			await authStore.login({
				email: email.value,
				password: password.value,
			});
			router.push("/dashboard");
		} else {
			error.value = result.error;
		}
	};
</script>
