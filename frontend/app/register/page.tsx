"use client";

import React, { useState } from "react";
import { registerUser } from "@/lib/api";
import Link from "next/link";
import { UserPlus, AlertCircle, CheckCircle } from "lucide-react";

export default function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"user" | "researcher">("user");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      await registerUser(email, password, role);
      setSuccessMessage("Account created successfully! Redirecting to login...");
      setTimeout(() => {
        window.location.href = "/login";
      }, 1500);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(msg || "Registration failed. Check password requirements.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-12 bg-white rounded-xl shadow-md border border-gray-200 p-8 space-y-6 animate-fade-in">
      <div className="text-center space-y-2">
        <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mx-auto">
          <UserPlus className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Create SafeTriage Account</h1>
        <p className="text-xs text-gray-500">Register to save assessments or access research tools.</p>
      </div>

      {errorMessage && (
        <div role="alert" className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-800 text-xs flex items-start gap-2">
          <AlertCircle className="w-4 h-4 text-red-600 flex-shrink-0 mt-0.5" />
          <div>{errorMessage}</div>
        </div>
      )}

      {successMessage && (
        <div role="status" className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-800 text-xs flex items-start gap-2">
          <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
          <div>{successMessage}</div>
        </div>
      )}

      <form onSubmit={handleRegister} className="space-y-4 text-sm">
        <div className="space-y-1">
          <label htmlFor="reg-email" className="block text-xs font-semibold text-gray-700">
            Email Address
          </label>
          <input
            id="reg-email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            placeholder="newuser@safetriage.org"
          />
        </div>

        <div className="space-y-1">
          <label htmlFor="reg-password" className="block text-xs font-semibold text-gray-700">
            Password (Min 8 chars, 1 uppercase, 1 lowercase, 1 digit)
          </label>
          <input
            id="reg-password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            placeholder="••••••••••••"
          />
        </div>

        <div className="space-y-1">
          <label htmlFor="reg-role" className="block text-xs font-semibold text-gray-700">
            Account Role
          </label>
          <select
            id="reg-role"
            value={role}
            onChange={(e) => setRole(e.target.value as "user" | "researcher")}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-indigo-500 focus:outline-none"
          >
            <option value="user">Standard User (Triage & History)</option>
            <option value="researcher">Researcher (Evaluation & Benchmarks)</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-2.5 bg-indigo-600 text-white font-bold rounded-lg shadow hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-200 disabled:opacity-50 transition"
        >
          {isLoading ? "Creating Account..." : "Register"}
        </button>
      </form>

      <div className="text-center text-xs text-gray-500 pt-2">
        Already have an account?{" "}
        <Link href="/login" className="text-indigo-600 font-semibold hover:underline">
          Login here
        </Link>
      </div>
    </div>
  );
}
