// src/components/Topbar.jsx
import React from 'react';
import logo from '../Assets/logo_cortada.png';
import { FaUser } from 'react-icons/fa';
import { useNavigate } from 'react-router-dom';

export default function TopbarNoSearch() {

  const navigate = useNavigate();

  const handleGoDashboard = () => {
    navigate("/dashboard");
  };

  return (
    <header className="bg-white shadow px-4 py-2 flex items-start justify-between border-b-2 border-gray">
      {/* Logo */}
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

      {/* Ícone de perfil */}
      <div className="flex items-center space-x-4 self-center">
        <button className="rounded-full bg-gray-200 p-2 hover:bg-gray-300">
          <FaUser/>
          <span role="img" aria-label="profile"></span>
        </button>
      </div>
    </header>
  );
}
