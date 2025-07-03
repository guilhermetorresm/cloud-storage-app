"use client";
import React, { useState } from 'react'; // Importar useState aqui
import {
  Upload,
  LogOut,
  Image,
  Video,
  FileText,
  Music,
  Folder,
} from "lucide-react";
import { useNavigate } from "react-router-dom"; // Assumindo que você usa react-router-dom

import { UploadModal } from './UploadModal'; // Importar o seu componente UploadModal

export default function Sidebar() {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  const handleOpenUploadModal = () => {
    setIsUploadModalOpen(true);
  };

  const handleCloseUploadModal = () => {
    setIsUploadModalOpen(false);
  };

  const navigate = useNavigate();

  const handleExit = () => {
    console.log("Clicou em sair");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/");
  };

  const menuItems = [
    { icon: Folder, label: "Todos os arquivos" },
    { icon: Image, label: "Imagens" },
    { icon: Video, label: "Vídeos" },
    { icon: Music, label: "Áudios" },
    { icon: FileText, label: "Documentos" },
  ];

  return (
    <aside className="w-60 h-full bg-white border-r shadow-sm flex flex-col p-4 overflow-hidden">
      {/* Conteúdo principal */}
      <div className="space-y-1 flex-1">
        {/* Upload como primeiro item, estilizado */}
        <button
          className="w-full flex items-center justify-between px-2 py-2 rounded text-left bg-black hover:bg-gray-800"
          onClick={handleOpenUploadModal} // Adiciona o onClick para abrir o modal
        >
          <div className="flex items-center space-x-2">
            <Upload className="w-5 h-5 text-white" />
            <span className="text-white">Upload</span>
          </div>
        </button>

        {menuItems.map(({ icon: Icon, label, count }) => (
          <button
            key={label}
            className="w-full flex items-center justify-between px-2 py-2 hover:bg-gray-100 rounded text-left"
          >
            <div className="flex items-center space-x-2">
              <Icon className="w-5 h-5" />
              <span>{label}</span>
            </div>
            {count !== undefined && (
              <span className="bg-gray-200 text-sm text-gray-700 px-2 py-0.5 rounded-full">
                {count}
              </span>
            )}
          </button>
        ))}
      </div>
      <div>
        <hr className="my-4 border-gray-300" />
        <button
          onClick={handleExit}
          className="z-10 text-red-600 font-semibold flex items-center space-x-2 hover:underline w-full"
        >
          <LogOut />
          <span>Sair</span>
        </button>
      </div>

      {/* Renderiza o UploadModal */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={handleCloseUploadModal}
      />
    </aside>
  );
}