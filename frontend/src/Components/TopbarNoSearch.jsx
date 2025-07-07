// src/components/TopbarNoSearch.jsx
import React, { useEffect, useState } from "react";
import logo from "../Assets/logo_cortada.png";
import { FaUser } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { fetchWithAuth } from "../Utils/fetchWithAuth";

export default function TopbarNoSearch() {
  const navigate = useNavigate();
  const [profileImage, setProfileImage] = useState(null);

  const handleGoDashboard = () => {
    navigate("/dashboard");
  };

  const handleProfile = () => {
    navigate("/profileView");
  };

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

  return (
    <header className="bg-white shadow px-4 py-2 flex items-start justify-between border-b-2 border-gray">
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

      {/* Ícone ou imagem de perfil */}
      <div className="flex items-center space-x-4 justify-center h-full">
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
