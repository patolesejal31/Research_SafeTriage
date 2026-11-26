"use client";

import React from "react";
import { PhoneCall, AlertOctagon, X } from "lucide-react";

interface EmergencyModalProps {
  isOpen: boolean;
  onClose: () => void;
  reason?: string;
}

export function EmergencyModal({ isOpen, onClose, reason }: EmergencyModalProps) {
  if (!isOpen) return null;

  return (
    <div
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="emergency-modal-title"
      aria-describedby="emergency-modal-desc"
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-75 backdrop-blur-sm animate-fade-in"
    >
      <div className="relative w-full max-w-lg bg-white rounded-xl shadow-2xl border-4 border-red-600 overflow-hidden">
        {/* Header */}
        <div className="bg-red-600 px-6 py-4 flex items-center justify-between text-white">
          <div className="flex items-center space-x-3">
            <AlertOctagon className="w-8 h-8 text-white animate-pulse" aria-hidden="true" />
            <h2 id="emergency-modal-title" className="text-xl font-bold tracking-tight">
              CRITICAL EMERGENCY ALERT (Level 1)
            </h2>
          </div>
          <button
            onClick={onClose}
            aria-label="Dismiss Emergency Warning"
            className="text-white hover:text-red-200 focus:outline-none focus:ring-2 focus:ring-white rounded p-1"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          <div className="bg-red-50 border-l-4 border-red-600 p-4 rounded text-red-900 text-sm">
            <p className="font-semibold text-base mb-1">
              Immediate medical evaluation is strongly recommended.
            </p>
            <p id="emergency-modal-desc">
              Your reported symptoms indicate a potential high-risk condition requiring immediate in-person emergency care.
              {reason && <span className="block mt-2 font-medium">Flagged Presentation: {reason}</span>}
            </p>
          </div>

          <p className="text-gray-700 text-sm font-medium">
            Do not wait for further questions or self-assessment. Contact emergency medical services immediately:
          </p>

          {/* Action Buttons */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
            <a
              href="tel:112"
              className="flex items-center justify-center px-4 py-3 bg-red-600 text-white rounded-lg font-bold text-base shadow hover:bg-red-700 focus:outline-none focus:ring-4 focus:ring-red-300 transition"
              aria-label="Call National Emergency Service on 112"
            >
              <PhoneCall className="w-5 h-5 mr-2" aria-hidden="true" />
              Call 112 (National)
            </a>
            <a
              href="tel:108"
              className="flex items-center justify-center px-4 py-3 bg-red-700 text-white rounded-lg font-bold text-base shadow hover:bg-red-800 focus:outline-none focus:ring-4 focus:ring-red-300 transition"
              aria-label="Call Ambulance on 108"
            >
              <PhoneCall className="w-5 h-5 mr-2" aria-hidden="true" />
              Call 108 (Ambulance)
            </a>
          </div>

          <div className="pt-3 border-t border-gray-200 flex justify-end">
            <button
              onClick={onClose}
              type="button"
              className="text-xs text-gray-500 hover:text-gray-800 underline focus:outline-none focus:ring-1 focus:ring-gray-400 p-1"
            >
              I understand, continue viewing details
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
