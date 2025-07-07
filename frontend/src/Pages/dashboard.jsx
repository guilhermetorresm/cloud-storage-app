import { useEffect, useState } from "react";
import Topbar from "../Components/Topbar";
import Sidebar from "../Components/Sidebar";
import { FaBars, FaTimes } from "react-icons/fa";
import FileCard from "../Components/fileCard";
import { FileViewer } from "../Components/file-viewer";
import { fetchWithAuth } from "../Utils/fetchWithAuth";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const [arquivos, setArquivos] = useState([]);
  const [menuAberto, setMenuAberto] = useState(false);
  const [selectedFileId, setSelectedFileId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // 🔹 Carrega os arquivos iniciais ao entrar
  useEffect(() => {
    fetchArquivosPadrao();
  }, []);

  const fetchArquivosPadrao = async () => {
    setIsLoading(true);
    try {
      const response = await fetchWithAuth(
        `${process.env.REACT_APP_API_URL}/api/v1/files/list`
      );

      if (response.ok) {
        const data = await response.json();
        const adaptados = adaptarArquivos(data.files);
        setArquivos(adaptados);
      } else {
        if (response.status === 403 || response.status === 401) {
          localStorage.removeItem("authToken");
          navigate("/login");
        }
        console.error("Erro ao buscar arquivos padrão:", response.status);
      }
    } catch (err) {
      console.error("Erro ao carregar arquivos:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // 🔹 Atualiza a lista de arquivos com os resultados da busca
  const handleSearchResults = (resultados) => {
    const adaptados = adaptarArquivos(resultados);
    setArquivos(adaptados);
  };

  const adaptarArquivos = (lista) => {
    if (!Array.isArray(lista)) return [];

    return lista.map((item) => ({
      id: item.file_id,
      title: item.name,
      type: item.category,
      url: item.thumbnail_url,
      thumbnail_url: item.thumbnail_url,
      size: item.size,
      size_humanized: item.size_humanized,
      createdAt: new Date(item.created_at),
      uploadDate: new Date(item.created_at).toLocaleDateString("pt-BR"),
      description: item.description,
      tags: Array.isArray(item.tags) ? item.tags : [],
      duration: null,
    })).sort((a, b) => b.createdAt - a.createdAt);
  };

  const handleFileCardClick = (fileObject) => {
    setSelectedFileId(fileObject.id);
  };

  const handleCloseFileViewer = () => {
    setSelectedFileId(null);
  };

  const handleFileMetadataUpdate = (fileId, updatedMetadata) => {
    setArquivos((prev) =>
      prev.map((arquivo) =>
        arquivo.id === fileId ? { ...arquivo, ...updatedMetadata } : arquivo
      )
    );
  };

  return (
    <div className="flex flex-col h-screen">
      <Topbar onSearchResults={handleSearchResults} />

      <div className="sm:hidden flex items-center justify-between bg-white shadow p-4">
        <button
          onClick={() => setMenuAberto(true)}
          className="text-xl text-gray-700"
        >
          <FaBars />
        </button>
      </div>

      {menuAberto && (
        <div className="fixed inset-0 z-50 flex">
          <div className="w-64 bg-white shadow-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Menu</h2>
              <button
                onClick={() => setMenuAberto(false)}
                className="text-gray-600"
              >
                <FaTimes />
              </button>
            </div>
            <Sidebar />
          </div>
          <div
            className="flex-1 bg-black bg-opacity-40"
            onClick={() => setMenuAberto(false)}
          ></div>
        </div>
      )}

      <div className="flex flex-1 overflow-hidden">
        <div className="hidden sm:block">
          <Sidebar />
        </div>

        <main className="flex-1 bg-gray-100 p-4 sm:p-6 overflow-auto">
          <div className="max-w-6xl mx-auto min-h-full flex flex-col items-start justify-start">
            {isLoading ? (
              <p className="text-gray-500 text-center">Carregando arquivos...</p>
            ) : arquivos.length === 0 ? (
              <p className="text-gray-400 text-center text-lg">
                Nenhum arquivo encontrado.
              </p>
            ) : (
              <div
                className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6 w-full"
    
              >
                {arquivos.map((file) => (
                  <FileCard
                    key={file.id}
                    file={file}
                    onClick={handleFileCardClick}
                  />
                ))}
              </div>
            )}
          </div>
        </main>
      </div>

      {selectedFileId && (
        <FileViewer
          fileId={selectedFileId}
          onClose={handleCloseFileViewer}
          onMetadataUpdate={handleFileMetadataUpdate}
        />
      )}
    </div>
  );
}
