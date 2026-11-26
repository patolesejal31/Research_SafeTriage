import type { Metadata } from "next";
import "./globals.css";
import { EmergencyBanner } from "@/components/EmergencyBanner";
import { Navbar } from "@/components/Navbar";
import { DisclaimerFooter } from "@/components/DisclaimerFooter";

export const metadata: Metadata = {
  title: "SafeTriage — Preliminary Medical Symptom Triage Prototype",
  description:
    "MCA Dissertation Research Prototype. Hybrid NLP, deterministic rule engine, and LLM triage stratification. Non-diagnostic, non-prescriptive.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-slate-50 text-gray-900 min-h-screen flex flex-col font-sans antialiased">
        {/* 112 / 108 Emergency Banner Visible On Every Page */}
        <EmergencyBanner />
        <Navbar />

        <main id="main-content" className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        <DisclaimerFooter />
      </body>
    </html>
  );
}
