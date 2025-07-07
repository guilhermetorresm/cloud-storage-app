// src/components/Sidebar.jsx
"use client";
import React, { useState } from 'react';
import {
  Upload,
  LogOut,
  Image,
  Video,
  FileText, // Provavelmente não usado, mas mantido do seu código original
  Music,
  Folder,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import UploadModal from './UploadModal';

export default function Sidebar({
  files, // Recebe a lista de arquivos do pai
  loading, // Recebe o status de carregamento do pai
  error, // Recebe o status de erro do pai
  activeFilter, // Recebe o filtro ativo do pai
  onFilterChange, // Callback para quando um filtro é clicado
  onUploadSuccess // Callback para quando um upload é bem-sucedido
}) {
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

  // Função para lidar com o clique nos filtros
  const handleFilterClick = (filterType, fileApiType) => {
    // Chama a função passada via props pelo componente pai
    if (onFilterChange) {
      onFilterChange(filterType, fileApiType);
    }
  };

  // Função para lidar com o sucesso do upload
  const handleInternalUploadSuccess = () => {
    handleCloseUploadModal(); // Fecha o modal
    if (onUploadSuccess) {
      onUploadSuccess(); // Notifica o componente pai para recarregar os arquivos
    }
  };

  const menuItems = [
    { 
      icon: Folder, 
      label: "Todos os arquivos", 
      filterType: 'all',
      fileApiType: 'all' // Renomeado para evitar confusão com 'fileType' na API
    },
    { 
      icon: Image, 
      label: "Imagens", 
      filterType: 'images',
      fileApiType: 'image' 
    },
    { 
      icon: Video, 
      label: "Vídeos", 
      filterType: 'videos',
      fileApiType: 'video' 
    },
    { 
      icon: Music, 
      label: "Áudios", 
      filterType: 'audios',
      fileApiType: 'audio' 
    },
  ];

  return (
    <aside className="w-60 h-full bg-white border-r shadow-sm flex flex-col p-4 overflow-hidden">
      {/* Conteúdo principal */}
      <div className="space-y-1 flex-1">
        {/* Upload como primeiro item, estilizado */}
        <button
          className="w-full flex items-center justify-center px-2 py-2 rounded text-center bg-black hover:bg-gray-800 mb-4 mt-3"
          onClick={handleOpenUploadModal}
        >
          <div className="flex items-center space-x-2">
            <Upload className="w-5 h-5 text-white" />
            <span className="text-white">Upload</span>
          </div>
        </button>

        {/* Indicador de carregamento */}
        {loading && (
          <div className="text-center py-2 text-gray-500">
            Carregando...
          </div>
        )}

        {/* Mensagem de erro */}
        {error && (
          <div className="text-center py-2 text-red-500 text-sm">
            {error}
          </div>
        )}

        {menuItems.map(({ icon: Icon, label, filterType, fileApiType }) => (
          <button
            key={label}
            className={`w-full flex items-center px-2 py-2 rounded text-left transition-colors ${
              activeFilter === filterType 
                ? 'bg-blue-100 text-blue-700 border-l-4 border-blue-500' 
                : 'hover:bg-gray-100'
            }`}
            onClick={() => handleFilterClick(filterType, fileApiType)}
          >
            <div className="flex items-center space-x-2">
              <Icon className="w-5 h-5" />
              <span>{label}</span>
            </div>
          </button>
        ))}

        {/* Lista de arquivos */}
        <div className="mt-4 space-y-2">
          {/* A exibição da contagem de arquivos e a lista agora usam a prop 'files' */}
          {files && files.length > 0 && (
            <div className="text-sm text-gray-600 font-medium">
              {files.length} arquivo{files.length !== 1 ? 's' : ''} encontrado{files.length !== 1 ? 's' : ''}
            </div>
          )}
          
          <div className="max-h-64 overflow-y-auto space-y-1">
            {files && files.map((file, index) => (
              <div
                key={file.file_id || index} // Use file_id se disponível, é mais robusto
                className="flex items-center space-x-2 p-2 rounded hover:bg-gray-50 cursor-pointer"
              >
                <div className="w-4 h-4 bg-gray-300 rounded flex-shrink-0"></div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 truncate">
                    {file.name || `Arquivo ${index + 1}`}
                  </div>
                  <div className="text-xs text-gray-500">
                    {file.size_humanized || (file.size && `${(file.size / 1024).toFixed(1)} KB`)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
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
        onUploadSuccess={handleInternalUploadSuccess} // Usa a função interna que chama o callback pai
      />
    </aside>
  );
}