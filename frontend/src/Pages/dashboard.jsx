// Dashboard.jsx
import { useEffect, useState } from "react";
import Topbar from "../Components/Topbar";
import Sidebar from "../Components/Sidebar";
import {
  FaFilePdf,
  FaFileAudio,
  FaFileVideo,
  FaFileArchive,
  FaFileAlt,
  FaBars,
  FaTimes,
  FaImage,
} from "react-icons/fa";
import FileCard from "../Components/fileCard"; // Corrigido para 'FileCard' (F maiúsculo)
import { FileViewer } from "../Components/file-viewer"; // Corrigido para 'file-viewer'
import { fetchWithAuth } from "../Utils/fetchWithAuth";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const [arquivos, setArquivos] = useState([]);
  const [menuAberto, setMenuAberto] = useState(false);
  const [selectedFileId, setSelectedFileId] = useState(null); // Agora guarda apenas o ID
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchArquivos = async () => {
      setIsLoading(true);
      try {
        const response = await fetchWithAuth(
          `${process.env.REACT_APP_API_URL}/api/v1/files/list`
        );

        if (!response.ok) {
          const contentType = response.headers.get("content-type");
          if (contentType && contentType.includes("application/json")) {
            const errorData = await response.json();
            if (response.status === 403 || response.status === 401) {
              localStorage.removeItem('authToken');
              navigate('/login');
              throw new Error('Sessão expirada ou acesso negado. Por favor, faça login novamente.');
            }
            throw new Error(errorData.message || `Erro do servidor: ${response.status}`);
          } else {
            const errorText = await response.text();
            console.error("Resposta não-JSON do servidor:", errorText);
            throw new Error(`Erro inesperado do servidor: ${response.status}. Resposta não é JSON.`);
          }
        }

        const data = await response.json();

        const arquivosAdaptados = data.files.map((item) => {
            // Mapeamento para o FileCard (apenas as informações da lista)
            return {
                id: item.file_id, // Usar file_id como id
                title: item.name,
                type: item.category,
                url: item.thumbnail_url, // No FileCard, queremos a thumbnail_url para pré-visualização
                thumbnail_url: item.thumbnail_url, // Manter o nome para consistência, se necessário
                size: item.size,
                size_humanized: item.size_humanized,
                createdAt: new Date(item.created_at),
                // uploadDate: item.created_at, // O FileCard espera uma string já formatada
                uploadDate: new Date(item.created_at).toLocaleDateString("pt-BR"),
                description: item.description,
                tags: Array.isArray(item.tags) ? item.tags : (item.tags ? String(item.tags).split(',').map(tag => tag.trim()) : []),
                // A API de listagem não tem duration_humanized, então vamos deixar nulo aqui no FileCard
                duration: null, // Será preenchido pelo FileViewer
                // Outros campos detalhados não vêm na lista, então não os mapeamos aqui
            };
        });

        arquivosAdaptados.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
        setArquivos(arquivosAdaptados);
      } catch (error) {
        console.error("Erro ao carregar arquivos:", error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchArquivos();
  }, [navigate]);

  // handleFileCardClick agora passa apenas o ID para o FileViewer
  const handleFileCardClick = (fileObject) => {
    setSelectedFileId(fileObject.id); // Passa apenas o ID
  };

  const handleCloseFileViewer = () => {
    setSelectedFileId(null); // Limpa o ID para fechar o viewer
  };

  // Essa função ainda será chamada pelo FileViewer para atualizar a lista da Dashboard
  const handleFileMetadataUpdate = (fileId, updatedMetadata) => {
    setArquivos(prevArquivos =>
      prevArquivos.map(arquivo =>
        arquivo.id === fileId ? { ...arquivo, ...updatedMetadata } : arquivo
      )
    );
    // Se o file viewer estiver aberto e for o mesmo arquivo, atualize-o localmente também.
    // selectedFileId não é um objeto, então não podemos fazer setSelectedFileId(prev => ({ ...prev, ...updatedMetadata }));
    // Mas o FileViewer já tem seu próprio estado, então ele se atualiza internamente.
    // Não precisamos mexer no selectedFileId aqui, ele apenas indica QUAL ID está aberto.
  };

  return (
    <div className="flex flex-col h-screen">
      <Topbar />

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
          <div className="max-w-6xl mx-auto min-h-full flex flex-col items-center justify-center">
            {isLoading ? (
              <p className="text-gray-500 text-center">
                Carregando arquivos...
              </p>
            ) : arquivos.length === 0 ? (
              <p className="text-gray-400 text-center text-lg">
                Nenhum arquivo encontrado.
              </p>
            ) : (
              <div
                className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6 w-full"
                dir="rtl"
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

      {/* FileViewer agora recebe fileId e cuidará da busca de detalhes */}
      {selectedFileId && (
        <FileViewer
          fileId={selectedFileId} // <<< PASSA APENAS O ID AQUI >>>
          onClose={handleCloseFileViewer}
          onMetadataUpdate={handleFileMetadataUpdate}
        />
      )}
    </div>
  );
}