"use client";
import React, { useState, useEffect } from 'react';
import {
  Upload,
  LogOut,
  Image,
  Video,
  FileText,
  Music,
  Folder,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import  UploadModal  from './UploadModal';

export default function Sidebar() {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [activeFilter, setActiveFilter] = useState('all');
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  // Função para buscar arquivos da API
  const fetchFilesByType = async (fileType) => {
    setLoading(true);
    setError(null);
    
    try {
      const token = localStorage.getItem("access_token");
      if (!token) {
        setError("Token de acesso não encontrado");
        return;
      }

      const url = fileType === 'all' 
        ? '/api/v1/files/list' 
        : `/api/v1/files/list?file_type=${fileType}`;

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Erro na requisição: ${response.status}`);
      }

      const data = await response.json();
      setFiles(data);
      
    } catch (error) {
      console.error('Erro ao buscar arquivos:', error);
      setError('Erro ao carregar arquivos');
    } finally {
      setLoading(false);
    }
  };

  // Carrega todos os arquivos ao montar o componente
  useEffect(() => {
    fetchFilesByType('all');
  }, []);

  // Função para lidar com o clique nos filtros
  const handleFilterClick = (filterType, fileType) => {
    setActiveFilter(filterType);
    fetchFilesByType(fileType);
  };

  // Função para lidar com o sucesso do upload
  const handleUploadSuccess = () => {
    // Recarrega os arquivos após um upload bem-sucedido
    fetchFilesByType(activeFilter === 'all' ? 'all' : menuItems.find(item => item.filterType === activeFilter)?.fileType);
  };

  const menuItems = [
    { 
      icon: Folder, 
      label: "Todos os arquivos", 
      filterType: 'all',
      fileType: 'all' 
    },
    { 
      icon: Image, 
      label: "Imagens", 
      filterType: 'images',
      fileType: 'image' 
    },
    { 
      icon: Video, 
      label: "Vídeos", 
      filterType: 'videos',
      fileType: 'video' 
    },
    { 
      icon: Music, 
      label: "Áudios", 
      filterType: 'audios',
      fileType: 'audio' 
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

        {menuItems.map(({ icon: Icon, label, filterType, fileType }) => (
          <button
            key={label}
            className={`w-full flex items-center px-2 py-2 rounded text-left transition-colors ${
              activeFilter === filterType 
                ? 'bg-blue-100 text-blue-700 border-l-4 border-blue-500' 
                : 'hover:bg-gray-100'
            }`}
            onClick={() => handleFilterClick(filterType, fileType)}
          >
            <div className="flex items-center space-x-2">
              <Icon className="w-5 h-5" />
              <span>{label}</span>
            </div>
          </button>
        ))}

        {/* Lista de arquivos */}
        <div className="mt-4 space-y-2">
          {files.length > 0 && (
            <div className="text-sm text-gray-600 font-medium">
              {files.length} arquivo{files.length !== 1 ? 's' : ''} encontrado{files.length !== 1 ? 's' : ''}
            </div>
          )}
          
          <div className="max-h-64 overflow-y-auto space-y-1">
            {files.map((file, index) => (
              <div
                key={file.id || index}
                className="flex items-center space-x-2 p-2 rounded hover:bg-gray-50 cursor-pointer"
              >
                <div className="w-4 h-4 bg-gray-300 rounded flex-shrink-0"></div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium text-gray-900 truncate">
                    {file.name || file.filename || `Arquivo ${index + 1}`}
                  </div>
                  <div className="text-xs text-gray-500">
                    {file.size && `${(file.size / 1024).toFixed(1)} KB`}
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
        onUploadSuccess={handleUploadSuccess}
      />
    </aside>
  );
}