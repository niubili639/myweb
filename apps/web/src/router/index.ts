import { createRouter, createWebHistory } from "vue-router";
import Home from "@/views/Home.vue";
import Login from "@/views/Login.vue";
import Register from "@/views/Register.vue";
import Ai from "@/views/Ai.vue";
import Couple from "@/views/Couple.vue";
import Album from "@/views/Album.vue";
import Notes from "@/views/Notes.vue";
import Settings from "@/views/Settings.vue";
import { useAuthStore } from "@/stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "Login", component: Login },
    { path: "/register", name: "Register", component: Register },
    { path: "/", name: "Home", component: Home },
    { path: "/ai", name: "Ai", component: Ai },
    { path: "/couple", name: "Couple", component: Couple },
    { path: "/album", name: "Album", component: Album },
    { path: "/notes", name: "Notes", component: Notes },
    { path: "/settings", name: "Settings", component: Settings },
  ],
});

const publicPages = ["Login", "Register"];

router.beforeEach((to, _from, next) => {
  const auth = useAuthStore();
  if (!publicPages.includes(to.name as string) && !auth.token) {
    return next({ name: "Login" });
  }
  if (publicPages.includes(to.name as string) && auth.token && to.name === "Login") {
    return next({ name: "Home" });
  }
  return next();
});

export default router;
