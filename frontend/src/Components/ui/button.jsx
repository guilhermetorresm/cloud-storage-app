"use client";

import React from "react";

export function Button({ children, variant = "primary", onClick, type = "button", className = "", disabled = false }) {
  const baseClasses = "w-full py-3 px-4 rounded-lg font-medium transition-colors duration-200";

  const variantClasses = {
    primary: "bg-black text-white hover:bg-gray-800",
    secondary: "bg-black text-white hover:bg-gray-800",
  };

  const disabledClasses = "bg-gray-400 text-gray-700 cursor-not-allowed";

  return (
    <button
      type={type}
      onClick={onClick}
      className={`${baseClasses} ${
        disabled ? disabledClasses : variantClasses[variant]
      } ${className}`}
      disabled={disabled}
    >
      {children}
    </button>
  );
}
