import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { useAuthStore } from "@/stores/authStore";
import { useThemeStore } from "@/stores/themeStore";
import { Toaster } from "sonner";
import { useEffect } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { EditorPage } from "@/pages/EditorPage";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";

function DashboardPage() {
  return <div className="p-6"><h1 className="text-2xl font-bold">Dashboard</h1><p className="text-muted-foreground mt-2">Coming soon...</p></div>;
}

function JobHistoryPage() {
  return <div className="p-6"><h1 className="text-2xl font-bold">Job History</h1><p className="text-muted-foreground mt-2">Coming soon...</p></div>;
}

export default function App() {
  const { fetchUser } = useAuthStore();
  const { theme } = useThemeStore();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    fetchUser();
  }, []);

  return (
    <BrowserRouter>
      <Toaster position="bottom-right" theme="system" />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/editor" element={<EditorPage />} />
          <Route path="/jobs" element={<JobHistoryPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
