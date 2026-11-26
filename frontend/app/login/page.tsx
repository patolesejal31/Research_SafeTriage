"use client";

import React, { useState } from "react";
import { loginUser } from "@/lib/api";
import { setStoredToken } from "@/lib/auth";
import Link from "next/link";
import { LogIn, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const res = await loginUser(email, password);
      setStoredToken(res.access_token, res.user);
      window.location.href = res.user.role === "researcher" ? "/dashboard" : "/";
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(msg || "Login failed. Please check credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSeedFill = (role: "user" | "researcher") => {
    if (role === "user") {
      setEmail("user@example.com");
      setPassword("UserPassword123!");
    } else {
      setEmail("researcher@example.com");
      setPassword("ResearcherPassword123!");
    }
  };

  return (
    <div className="max-w-md mx-auto my-12 bg-white rounded-xl shadow-md border border-gray-200 p-8 space-y-6 animate-fade-in">
      <div className="text-center space-y-2">
        <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto">
          <LogIn className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Login to SafeTriage</h1>
        <p className="text-xs text-gray-500">Access your saved assessments or researcher dashboard.</p>
      </div>

      {errorMessage && (
        <div role="alert" className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-800 text-xs flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
          <div>{errorMessage}</div>
        </div>
      )}

      <form onSubmit={handleLogin} className="space-y-4 text-sm">
        <div className="space-y-1">
          <label htmlFor="login-email" className="block text-xs font-semibold text-gray-700">
            Email Address
          </label>
          <input
            id="login-email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            placeholder="user@example.com"
          />
        </div>

        <div className="space-y-1">
          <label htmlFor="login-password" className="block text-xs font-semibold text-gray-700">
            Password
          </label>
          <input
            id="login-password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            placeholder="••••••••••••"
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-2.5 bg-indigo-600 text-white font-bold rounded-lg shadow hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-200 disabled:opacity-50 transition"
        >
          {isLoading ? "Signing in..." : "Sign In"}
        </button>
      </form>

      {/* Seed Accounts Quick Fill */}
      <div className="pt-4 border-t border-gray-100 text-xs space-y-2">
        <span className="text-gray-500 block font-semibold">Development Seed Accounts:</span>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => handleSeedFill("user")}
            className="flex-1 py-1.5 px-2 bg-gray-50 border border-gray-200 rounded text-gray-700 hover:bg-gray-100 transition"
          >
            User Demo
          </button>
          <button
            type="button"
            onClick={() => handleSeedFill("researcher")}
            className="flex-1 py-1.5 px-2 bg-indigo-50 border border-indigo-200 rounded text-indigo-800 font-medium hover:bg-indigo-100 transition"
          >
            Researcher Demo
          </button>
        </div>
      </div>

      <div className="text-center text-xs text-gray-500 pt-2">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="text-indigo-600 font-semibold hover:underline">
          Register here
        </Link>
      </div>
    </div>
  );
}
