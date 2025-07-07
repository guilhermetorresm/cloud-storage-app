// src/components/Topbar.jsx
import React, { useEffect, useState } from "react";
import { Search } from "lucide-react";
import logo from "../Assets/logo_cortada.png";
import { useNavigate } from "react-router-dom";
import { FaUser } from "react-icons/fa";
import { fetchWithAuth } from "../Utils/fetchWithAuth";

export default function Topbar() {
  const navigate = useNavigate();
  const [profileImage, setProfileImage] = useState(null);

  useEffect(() => {
    async function fetchProfileImage() {
      try {
        const response = await fetchWithAuth(
          `${process.env.REACT_APP_API_URL}/api/v1/users/me`
        );

        if (response.ok) {
          const data = await response.json();
          setProfileImage(data.profile_image || null);
        }
      } catch (err) {
        console.error("Erro ao carregar imagem do perfil:", err);
      }
    }

    fetchProfileImage();
  }, []);

  const handleProfile = () => {
    navigate("/profileView");
  };

  const handleGoDashboard = () => {
    navigate("/dashboard");
  };

  return (
    <header className="bg-white shadow px-4 py-2 flex items-center justify-between border-b-2 border-gray w-full">
      {/* Logo clicável */}
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

      {/* Barra de pesquisa */}
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

      {/* Ícone ou imagem de perfil */}
      <div className="flex items-center space-x-4">
        <button
          onClick={handleProfile}
          className="w-10 h-10 rounded-full bg-gray-200 hover:bg-gray-300 overflow-hidden flex items-center justify-center"
        >
          {profileImage ? (
            <img
              src={profileImage}
              alt="Perfil"
              className="w-full h-full object-cover rounded-full"
            />
          ) : (
            <FaUser className="text-gray-600 text-lg" />
          )}
        </button>
      </div>
    </header>
  );
}
