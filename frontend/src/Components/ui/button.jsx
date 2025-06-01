"use client";

import React from "react";

export function Button({ children, variant = "primary", onClick, type = "button", className = "" }) {
  const baseClasses = "w-full py-3 px-4 rounded-lg font-medium transition-colors duration-200";

  const variantClasses = {
    primary: "bg-black text-white hover:bg-gray-800",
    secondary: "bg-black text-white hover:bg-gray-800",
  };

  return (
    <button
      type={type}
      onClick={onClick}
      className={`${baseClasses} ${variantClasses[variant]} ${className}`}
    >
      {children}
    </button>
  );
}
