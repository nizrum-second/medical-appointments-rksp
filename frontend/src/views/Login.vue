<template>
	<div class="min-h-screen flex items-center justify-center px-4 py-10">
		<div class="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
			<div class="mb-8 text-center">
				<h2 class="text-3xl font-semibold tracking-tight text-slate-900">
					Вход в систему
				</h2>
				<p class="mt-2 text-sm text-slate-500">
					Безопасный доступ к онлайн-записям пациентов
				</p>
			</div>
			<form
				class="space-y-5"
				@submit.prevent="handleLogin">
				<div class="space-y-4">
					<input
						v-model="email"
						type="email"
						required
						class="input-field"
						placeholder="Адрес электронной почты" />
					<input
						v-model="password"
						type="password"
						required
						class="input-field"
						placeholder="Пароль" />
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
						Войти в аккаунт
					</button>
				</div>

				<div class="text-center">
					<router-link
						to="/register"
						class="text-sm font-medium text-blue-700 hover:text-blue-800">
						Нет аккаунта? Зарегистрироваться
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
	const email = ref("");
	const password = ref("");
	const error = ref("");

	const handleLogin = async () => {
		const result = await authStore.login({
			email: email.value,
			password: password.value,
		});

		if (result.success) {
			router.push("/dashboard");
		} else {
			error.value = result.error;
		}
	};
</script>
