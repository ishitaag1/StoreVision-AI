"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/services/api";
import { User } from "@/types";

export function useAuth(requireAuth: boolean = true) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const checkSession = async () => {
      try {
        const response = await api.get("/api/auth/me");
        setUser(response.data.user);
        setIsAuthenticated(true);
      } catch (error) {
        setUser(null);
        setIsAuthenticated(false);
        if (requireAuth) {
          router.push("/login");
        }
      } finally {
        setIsLoading(false);
      }
    };

    checkSession();
  }, [requireAuth, router]);

  const logout = async () => {
    try {
      await api.post("/api/auth/logout");
      setUser(null);
      setIsAuthenticated(false);
      router.push("/login");
    } catch (error) {
      console.error("Logout failed", error);
    }
  };

  return { user, isLoading, isAuthenticated, logout };
}