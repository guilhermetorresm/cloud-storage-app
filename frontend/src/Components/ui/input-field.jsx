"use client";

import React from "react";
import { User, Lock } from "lucide-react";

export function InputField({ type, placeholder, icon, value, onChange }) {
  const IconComponent = icon === "user" ? User : Lock;

  return (
    <div className="relative">
      <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">
        <IconComponent className="w-4 h-4" />
      </div>
      <input
        type={type}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
    </div>
  );
}
