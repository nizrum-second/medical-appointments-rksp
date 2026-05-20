import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

const routes = [
	{
		path: "/login",
		name: "Login",
		component: () => import("../views/Login.vue"),
		meta: { requiresGuest: true },
	},
	{
		path: "/register",
		name: "Register",
		component: () => import("../views/Register.vue"),
		meta: { requiresGuest: true },
	},
	{
		path: "/",
		redirect: "/dashboard",
	},
	{
		path: "/dashboard",
		name: "PatientDashboard",
		component: () => import("../views/PatientDashboard.vue"),
		meta: { requiresAuth: true, role: "patient" },
	},
	{
		path: "/doctors",
		name: "Doctors",
		component: () => import("../views/DoctorsList.vue"),
		meta: { requiresAuth: true, role: "patient" },
	},
	{
		path: "/book-appointment/:doctorId",
		name: "BookAppointment",
		component: () => import("../views/AppointmentBooking.vue"),
		meta: { requiresAuth: true, role: "patient" },
	},
	{
		path: "/my-appointments",
		name: "MyAppointments",
		component: () => import("../views/MyAppointments.vue"),
		meta: { requiresAuth: true, role: "patient" },
	},
	{
		path: "/doctor-dashboard",
		name: "DoctorDashboard",
		component: () => import("../views/DoctorDashboard.vue"),
		meta: { requiresAuth: true, role: "doctor" },
	},
	{
		path: "/doctor-schedule",
		name: "DoctorSchedule",
		component: () => import("../views/DoctorSchedule.vue"),
		meta: { requiresAuth: true, role: "doctor" },
	},
	{
		path: "/admin",
		name: "AdminDashboard",
		component: () => import("../views/AdminDashboard.vue"),
		meta: { requiresAuth: true, role: "admin" },
	},
	{
		path: "/admin/users",
		name: "AdminUsers",
		component: () => import("../views/AdminUsers.vue"),
		meta: { requiresAuth: true, role: "admin" },
	},
	{
		path: "/admin/doctors",
		name: "AdminDoctors",
		component: () => import("../views/AdminDoctors.vue"),
		meta: { requiresAuth: true, role: "admin" },
	},
	{
		path: "/admin/appointments",
		name: "AdminAppointments",
		component: () => import("../views/AdminAppointments.vue"),
		meta: { requiresAuth: true, role: "admin" },
	},
	{
		path: "/admin/services",
		name: "AdminServices",
		component: () => import("../views/ServicesManagement.vue"),
		meta: { requiresAuth: true, role: "admin" },
	},
	{
		path: "/services",
		name: "ServicesList",
		component: () => import("../views/ServicesList.vue"),
		meta: { requiresAuth: true, role: "patient" },
	},
];

const router = createRouter({
	history: createWebHistory(),
	routes,
});

router.beforeEach(async (to, from, next) => {
	const authStore = useAuthStore();

	if (authStore.isAuthenticated && !authStore.user) {
		await authStore.fetchUser();
	}

	if (to.meta.requiresGuest && authStore.isAuthenticated) {
		if (authStore.userRole === "admin") {
			next("/admin");
		} else if (authStore.userRole === "doctor") {
			next("/doctor-dashboard");
		} else {
			next("/dashboard");
		}
		return;
	}

	if (to.meta.requiresAuth && !authStore.isAuthenticated) {
		next("/login");
		return;
	}

	if (to.meta.role && authStore.userRole !== to.meta.role) {
		if (authStore.userRole === "admin") {
			next("/admin");
		} else if (authStore.userRole === "doctor") {
			next("/doctor-dashboard");
		} else {
			next("/dashboard");
		}
		return;
	}

	next();
});

export default router;
