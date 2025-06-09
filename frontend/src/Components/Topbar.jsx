// src/components/Topbar.jsx
import React from "react";
import { Search } from "lucide-react";
import logo from "../Assets/logo_cortada.png";
import { useNavigate } from "react-router-dom";
import { FaUser } from "react-icons/fa";

export default function Topbar() {
  const navigate = useNavigate();

  const handleProfile = () => {
    navigate("/profileView");
  };

  const handleGoDashboard = () => {
    navigate("/dashboard");
  };

  return (
    <header className="bg-white shadow px-4 py-2 flex items-center justify-between border-b-2 border-gray w-full">
      {/* Logo com click */}
      <div
        className="flex items-center space-x-3 cursor-pointer"
        onClick={handleGoDashboard}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            handleGoDashboard();
          }
        }}
        aria-label="Ir para dashboard"
      >
        <img
          src={logo}
          alt="Logo"
          className="h-8 sm:h-10 w-auto transition-all duration-300"
        />
      </div>

      {/* Barra de pesquisa compacta */}
      <div className="flex-1 mx-4 max-w-[400px]">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Pesquisar arquivos..."
            className="w-full px-9 py-1.5 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>
      </div>

      {/* Ícone de perfil */}
      <div className="flex items-center space-x-4 self">
        <button
          onClick={handleProfile}
          className="rounded-full bg-gray-200 p-2 hover:bg-gray-300"
        >
          <FaUser />
        </button>
      </div>
    </header>
  );
}
