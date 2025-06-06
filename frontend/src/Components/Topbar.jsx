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

  return (
    <header className="bg-white shadow px-4 py-2 flex items-center justify-between border-b-2 border-gray flex-wrap gap-3 sm:gap-0">
  {/* Logo */}
  <div className="flex items-center space-x-3">
    <img
      src={logo}
      alt="Logo"
      className="h-10 w-25 transition-all duration-300"
    />
  </div>

  {/* Barra de pesquisa */}
  <div className="flex-1 mx-1 translate-x-16 min-w-[200px]">
    <div className="relative w-80 max-w-screen-sm sm:min-w-md">
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
      <input
        type="text"
        placeholder="Pesquisar arquivos..."
        className="w-full px-10 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
      />
    </div>
  </div>

  {/* Ícone de perfil */}
  <div className="flex items-center space-x-4">
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
