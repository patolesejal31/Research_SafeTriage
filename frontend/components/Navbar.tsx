"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldCheck, History, BarChart3, LogIn, LogOut, User, PhoneCall } from "lucide-react";
import { clearStoredAuth, getStoredUser } from "@/lib/auth";
import { UserProfile } from "@/types/assessment";

export function Navbar() {
  const pathname = usePathname();
  const [user, setUser] = useState<UserProfile | null>(null);

  useEffect(() => {
    setUser(getStoredUser());
  }, [pathname]);

  const handleLogout = () => {
    clearStoredAuth();
    setUser(null);
    window.location.href = "/";
  };

  const navLinks = [
    { href: "/", label: "Triage", icon: ShieldCheck },
    { href: "/history", label: "History", icon: History },
    { href: "/dashboard", label: "Research Dashboard", icon: BarChart3, researcherOnly: true },
  ];

  return (
    <nav aria-label="Main Navigation" className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo & Emergency Quick Badge */}
          <div className="flex items-center space-x-4">
            <Link
              href="/"
              className="flex items-center space-x-2 text-indigo-700 font-extrabold text-xl tracking-tight hover:text-indigo-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded p-1"
            >
              <ShieldCheck className="w-7 h-7 text-indigo-600" aria-hidden="true" />
              <span>SafeTriage</span>
            </Link>

            <span className="hidden md:inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-100 text-red-800">
              <PhoneCall className="w-3 h-3 mr-1" />
              112 / 108
            </span>
          </div>

          {/* Links */}
          <div className="flex items-center space-x-1 sm:space-x-3">
            {navLinks.map((link) => {
              if (link.researcherOnly && user?.role !== "researcher") {
                return null;
              }
              const isActive = pathname === link.href;
              const Icon = link.icon;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`inline-flex items-center px-3 py-2 rounded-md text-sm font-medium transition focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                    isActive
                      ? "bg-indigo-50 text-indigo-700 font-semibold"
                      : "text-gray-700 hover:bg-gray-100 hover:text-gray-900"
                  }`}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon className="w-4 h-4 mr-1.5" aria-hidden="true" />
                  {link.label}
                </Link>
              );
            })}

            {/* Auth status */}
            {user ? (
              <div className="flex items-center space-x-2 pl-2 border-l border-gray-200">
                <span className="hidden sm:inline-flex items-center text-xs text-gray-600 font-medium bg-gray-100 px-2.5 py-1 rounded-full">
                  <User className="w-3 h-3 mr-1" />
                  {user.email.split("@")[0]} ({user.role})
                </span>
                <button
                  onClick={handleLogout}
                  className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 rounded-md text-xs font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                  aria-label="Log out of session"
                >
                  <LogOut className="w-3.5 h-3.5 mr-1" />
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2 pl-2 border-l border-gray-200">
                <Link
                  href="/login"
                  className="inline-flex items-center px-3 py-1.5 border border-indigo-600 rounded-md text-xs font-medium text-indigo-600 hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
                >
                  <LogIn className="w-3.5 h-3.5 mr-1" />
                  Login
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
