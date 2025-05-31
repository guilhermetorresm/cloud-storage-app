// src/components/Topbar.jsx
import React from 'react';

import logo from '../Assets/logo_cortada.png';

export default function Topbar() {
  return (
    <header className="bg-white shadow px-4 py-2 flex items-start justify-between border-b-2 border-gray">
      {/* Logo */}
      <div className="flex items-center space-x-3">
        <img src={logo} alt="Logo" className="h-10 w-25" />
      </div>

      {/* Ícone de perfil */}
      <div className="flex items-center space-x-4">
        <button className="rounded-full bg-gray-200 p-2 hover:bg-gray-300">
          <span role="img" aria-label="profile">👤</span>
        </button>
      </div>
    </header>
  );
}
