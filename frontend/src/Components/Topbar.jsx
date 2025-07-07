// src/components/Topbar.jsx

import React, { useEffect, useState } from "react";

import { Search } from "lucide-react";
import logo from "../Assets/logo_cortada.png";
import { useNavigate } from "react-router-dom";
import { FaUser } from "react-icons/fa";

import { fetchWithAuth } from "../Utils/fetchWithAuth";

export default function Topbar({ onSearchResults }) {
  const navigate = useNavigate();
  const [profileImage, setProfileImage] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(false);

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

  // Função para buscar arquivos por nome E/OU tags
  const searchFiles = async (searchQuery) => {
    if (!searchQuery.trim()) {
      // Se a busca estiver vazia, retorna uma lista vazia ou todos os arquivos, dependendo do desejado
      if (onSearchResults) {
        onSearchResults([]); // Retorna uma lista vazia para busca em branco
      }
      return;
    }

    setLoading(true);

    try {
      let url = `${process.env.REACT_APP_API_URL}/api/v1/files/list`;
      const queryParams = [];
      const encodedSearchTerm = encodeURIComponent(searchQuery.trim());

      // Adiciona o termo de busca para o nome do arquivo
      queryParams.push(`file_name=${encodedSearchTerm}`);
      
      // Adiciona o termo de busca para as tags. 
      // A API já espera tags separadas por vírgulas, mas se o usuário digitar uma única palavra,
      // ela pode ser usada como uma única tag para busca parcial.
      queryParams.push(`tags=${encodedSearchTerm}`);

      if (queryParams.length > 0) {
        url += `?${queryParams.join('&')}`;
      }

      // --- Adicione este console.log para depurar a URL ---
      console.log("URL da busca enviada:", url);
      // ----------------------------------------------------

      const response = await fetchWithAuth(url);

      if (response.ok) {
        const data = await response.json();
        // O JSON de retorno tem um array 'files' dentro dele
        if (onSearchResults) {
          onSearchResults(data.files || []);
        }
      } else {
        console.error("Erro ao buscar arquivos:", response.status);
        if (onSearchResults) {
          onSearchResults([]);
        }
      }
    } catch (error) {
      console.error("Erro ao buscar arquivos:", error);
      if (onSearchResults) {
        onSearchResults([]);
      }
    } finally {
      setLoading(false);
    }
  };


  const handleProfile = () => {
    navigate("/profileView");
  };

  const handleGoDashboard = () => {
    navigate("/dashboard");
  };


  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    searchFiles(searchTerm);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      searchFiles(searchTerm);
    }
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
        <form onSubmit={handleSearchSubmit} className="relative w-full">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Pesquisar por nome ou tags..."
            value={searchTerm}
            onChange={handleSearchChange}
            onKeyPress={handleKeyPress}
            className="w-full px-9 py-1.5 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            disabled={loading}
          />
          {loading && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}
        </form>
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

