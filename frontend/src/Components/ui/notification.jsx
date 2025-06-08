import { useEffect } from "react";

export function Notification({ message, type = "error", onClose }) {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose(); // Fecha automaticamente após 3 segundos
    }, 3000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const colors = {
    error: "bg-red-500",
    success: "bg-green-500",
    info: "bg-blue-500",
  };

  return (
    <div
      className={`fixed top-4 left-1/2 transform -translate-x-1/2 z-50 px-6 py-3 text-white font-medium rounded-xl shadow-lg ${colors[type]}`}	
    >
      {message}
    </div>
  );
}
