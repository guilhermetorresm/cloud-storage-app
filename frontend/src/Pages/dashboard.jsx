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
import { FileViewer } from "../Components/file-viewer";
import { fetchWithAuth } from "../Utils/fetchWithAuth";
import { useNavigate } from "react-router-dom";

const FileCard = ({ file, onClick }) => {
  const getTypeColor = (type) => {
    switch (type) {
      case "video":
        return "bg-blue-100 text-blue-800";
      case "image":
        return "bg-green-100 text-green-800";
      case "audio":
        return "bg-purple-100 text-purple-800";
      case "pdf":
        return "bg-red-100 text-red-800";
      case "text":
        return "bg-yellow-100 text-yellow-800";
      case "zip":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case "video":
        return <FaFileVideo className="text-blue-500" />;
      case "image":
        return <FaImage className="text-green-500" />;
      case "audio":
        return <FaFileAudio className="text-purple-500" />;
      case "pdf":
        return <FaFilePdf className="text-red-500" />;
      case "text":
        return <FaFileAlt className="text-yellow-500" />;
      case "zip":
        return <FaFileArchive className="text-gray-500" />;
      default:
        return <FaFileAlt className="text-gray-500" />;
    }
  };

  return (
    <div
      className="relative bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 cursor-pointer"
      onClick={() => onClick(file)}
    >
      <div className="relative bg-gray-200 h-32 w-50 flex items-center justify-center">
        {file.type === "image" && file.url ? (
          <img
            src={file.url}
            alt={file.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-5xl text-gray-400">{getTypeIcon(file.type)}</div>
        )}
        <div
          className={`absolute top-2 left-2 px-2 py-1 rounded-full text-xs font-semibold ${getTypeColor(
            file.type
          )}`}
        >
          {file.type}
        </div>
        {(file.type === "video" || file.type === "audio") && file.duration && (
          <div className="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded">
            {file.duration}
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="text-base font-semibold text-gray-800 truncate mb-1">
          {file.title}
        </h3>
        <div className="flex justify-between text-xs text-gray-600 mt-2">
          {file.size && <p>{file.size}</p>}
          {file.uploadDate && <p>{file.uploadDate}</p>}
        </div>
      </div>
    </div>
  );
};

export default function Dashboard() {
  const [arquivos, setArquivos] = useState([]);
  const [menuAberto, setMenuAberto] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchArquivos = async () => {
      try {
        const response = await fetchWithAuth(
          `${process.env.REACT_APP_API_URL}/api/v1/files/list`
        );

        if (!response.ok) {
          const contentType = response.headers.get("content-type");
          if (contentType && contentType.includes("application/json")) {
            const errorData = await response.json();
            throw new Error(errorData.message || `Erro do servidor: ${response.status}`);
          } else {
            const errorText = await response.text();
            console.error("Resposta não-JSON do servidor:", errorText);

            if (response.status === 403 || response.status === 401) {
              localStorage.removeItem('authToken');
              navigate('/login');
              throw new Error('Sessão expirada ou acesso negado. Por favor, faça login novamente.');
            }
            throw new Error(`Erro inesperado do servidor: ${response.status}. Resposta não é JSON.`);
          }
        }

        const data = await response.json();

        const arquivosAdaptados = data.files.map((item) => ({
          id: item.file_id,
          title: item.name,
          type: item.category,
          url: item.thumbnail_url || null,
          size: item.size_humanized,
          createdAt: new Date(item.created_at),
          uploadDate: new Date(item.created_at).toLocaleDateString("pt-BR"),
          duration: null,
        }));

        // **MUDANÇA AQUI:** Invertendo a ordem de sort para do mais ANTIGO para o mais NOVO
        arquivosAdaptados.sort((a, b) => a.createdAt.getTime() - b.createdAt.getTime());

        setArquivos(arquivosAdaptados);
      } catch (error) {
        console.error("Erro ao carregar arquivos:", error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchArquivos();
  }, [navigate]);

  const handleFileCardClick = (file) => setSelectedFile(file);
  const handleCloseFileViewer = () => setSelectedFile(null);

  return (
    <div className="flex flex-col h-screen">
      <Topbar />

      {/* Mobile menu */}
      <div className="sm:hidden flex items-center justify-between bg-white shadow p-4">
        <button
          onClick={() => setMenuAberto(true)}
          className="text-xl text-gray-700"
        >
          <FaBars />
        </button>
      </div>

      {/* Sidebar (mobile) */}
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

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        <div className="hidden sm:block">
          <Sidebar />
        </div>

        <main className="flex-1 bg-gray-100 p-4 sm:p-6 overflow-auto">
          <div className="max-w-6xl mx-auto min-h-full flex items-center justify-center">
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
                dir="rtl" // Mantido para que o fluxo do layout seja da direita para a esquerda
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

      {/* File Viewer */}
      {selectedFile && (
        <FileViewer file={selectedFile} onClose={handleCloseFileViewer} />
      )}
    </div>
  );
}