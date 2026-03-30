import type { LoginRequest, MessageResponse, RegisterRequest, TokenResponse, User } from "@/types/auth";
import api from "./api";

export const authService = {
  register: (data: RegisterRequest) => api.post<User>("/auth/register", data).then((r) => r.data),
  login: (data: LoginRequest) => api.post<TokenResponse>("/auth/login", data).then((r) => r.data),
  refresh: () => api.post<TokenResponse>("/auth/refresh").then((r) => r.data),
  logout: () => api.post<MessageResponse>("/auth/logout").then((r) => r.data),
  logoutAll: () => api.post<MessageResponse>("/auth/logout-all").then((r) => r.data),
  me: () => api.get<User>("/auth/me").then((r) => r.data),
  verifyEmail: (code: string) => api.post<MessageResponse>("/auth/verify-email", { code }).then((r) => r.data),
  resendVerification: () => api.post<MessageResponse>("/auth/resend-verification").then((r) => r.data),
  forgotPassword: (email: string) => api.post<MessageResponse>("/auth/forgot-password", { email }).then((r) => r.data),
  resetPassword: (data: { email: string; token: string; new_password: string }) => api.post<MessageResponse>("/auth/reset-password", data).then((r) => r.data),
};
