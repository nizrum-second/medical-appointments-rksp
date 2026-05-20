import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), '');
	const backendUrl =
		env.VITE_API_URL || env.BACKEND_URL || "http://backend:8000";

	return {
		plugins: [vue()],
		server: {
			port: 3000,
			proxy: {
				'/api': {
					target: backendUrl,
					changeOrigin: true,
					secure: false,
				},
			},
		},
	};
});
