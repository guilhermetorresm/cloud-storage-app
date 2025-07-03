import { useEffect, useState } from "react";
import Topbar from "../Components/Topbar";
import Sidebar from "../Components/Sidebar";
import {
  FaFilePdf,
  FaFileAudio,
  FaFileVideo,
  FaFileArchive,
  FaFileAlt,
  FaArrowLeft,
  FaArrowRight,
  FaBars,
  FaTimes,
  FaImage, // Não esqueça de importar FaImage aqui também!
} from "react-icons/fa";

// Mock de arquivos (ATUALIZADO - USE ESTE)
const mockArquivos = [
  {
    id: "1",
    nome: "Product Demo Video",
    tipo: "video",
    url: "https://via.placeholder.com/150x100?text=Video+Placeholder",
    tamanho: "45.2 MB",
    dataUpload: "14/01/2024",
    duracao: "3:24",
    categoria: "Educational",
  },
  {
    id: "2",
    nome: "Company Logo",
    tipo: "image",
    url: "https://via.placeholder.com/150x100?text=Logo",
    tamanho: "2.1 MB",
    dataUpload: "13/01/2024",
    dimensoes: "1920x1080",
  },
  {
    id: "3",
    nome: "Presentation Audio",
    tipo: "audio",
    url: "https://via.placeholder.com/150x100?text=Audio+Placeholder",
    tamanho: "12.8 MB",
    dataUpload: "12/01/2024",
    duracao: "15:30",
    categoria: "Business",
  },
  {
    id: "4",
    nome: "Project Proposal",
    tipo: "pdf",
    tamanho: "8.5 MB",
    dataUpload: "10/01/2024",
    categoria: "Documentation",
  },
  {
    id: "5",
    nome: "Meeting Notes",
    tipo: "text",
    tamanho: "0.2 MB",
    dataUpload: "09/01/2024",
    categoria: "Notes",
  },
  {
    id: "6",
    nome: "Website Backup",
    tipo: "zip",
    tamanho: "120 MB",
    dataUpload: "08/01/2024",
    categoria: "Backup",
  },
  // Adicione mais arquivos para ver a paginação e o layout
  {
    id: "7",
    nome: "Marketing Campaign Report",
    tipo: "pdf",
    tamanho: "15.7 MB",
    dataUpload: "07/01/2024",
    categoria: "Marketing",
  },
  {
    id: "8",
    nome: "Team Meeting Video",
    tipo: "video",
    url: "https://via.placeholder.com/150x100?text=Team+Video",
    tamanho: "88.3 MB",
    dataUpload: "06/01/2024",
    duracao: "45:10",
    categoria: "Internal",
  },
  {
    id: "9",
    nome: "Product Launch Images",
    tipo: "image",
    url: "https://via.placeholder.com/150x100?text=Launch+Pics",
    tamanho: "5.5 MB",
    dataUpload: "05/01/2024",
    dimensoes: "1280x720",
    categoria: "Marketing Assets",
  },
];

// Componente de visualização dos arquivos (ATUALIZADO - USE ESTE)
const FileCard = ({ file }) => {
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
    <div className="relative bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300">
      <div className="relative bg-gray-200 h-32 flex items-center justify-center">
        {file.tipo === "image" && file.url ? (
          <img
            src={file.url}
            alt={file.nome}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-5xl text-gray-400">{getTypeIcon(file.tipo)}</div>
        )}

        <div
          className={`absolute top-2 left-2 px-2 py-1 rounded-full text-xs font-semibold ${getTypeColor(
            file.tipo
          )}`}
        >
          {file.tipo}
        </div>

        {(file.tipo === "video" || file.tipo === "audio") && file.duracao && (
          <div className="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded">
            {file.duracao}
          </div>
        )}
      </div>

      <div className="p-4">
        <h3 className="text-base font-semibold text-gray-800 truncate mb-1">
          {file.nome}
        </h3>
        <div className="text-gray-600 text-sm">
          {file.tamanho && <p>{file.tamanho}</p>}
          {file.dimensoes && <p>{file.dimensoes}</p>}
          {file.dataUpload && <p>{file.dataUpload}</p>}
          {file.categoria && (
            <p className="text-blue-500 text-xs mt-1">{file.categoria}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default function Dashboard() {
  const [arquivos, setArquivos] = useState([]);
  const [menuAberto, setMenuAberto] = useState(false);

  useEffect(() => {
    // Simula o carregamento dos arquivos
    setTimeout(() => {
      setArquivos(mockArquivos);
    }, 500);
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      <Topbar />

      {/* Botão hambúrguer para mobile */}
      <div className="sm:hidden flex items-center justify-between bg-white shadow p-4">
        <button
          onClick={() => setMenuAberto(true)}
          className="text-xl text-gray-700"
        >
          <FaBars />
        </button>
      </div>

      {/* Menu lateral deslizante (mobile) */}
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

      {/* Conteúdo principal com sidebar (visível em telas maiores) */}
      <div className="flex flex-1">
        <div className="hidden sm:block">
          <Sidebar />
        </div>

        <main className="flex-1 bg-gray-100 p-4 sm:p-6 overflow-auto">
          <div className="max-w-6xl mx-auto">
            {arquivos.length === 0 ? (
              <p className="text-center">Carregando arquivos...</p>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
                {arquivos.map((file) => (
                  <FileCard key={file.id} file={file} />
                ))}
              </div>
            )}
          </div>

          {/* Paginação (mantida como está, mas você pode estilizá-la mais tarde) */}
          <div className="flex justify-center items-center mt-6 space-x-2">
            <button className="p-2 bg-white rounded-full shadow hover:bg-gray-200">
              <FaArrowLeft />
            </button>
            <div className="flex space-x-1 text-sm">
              <span className="px-2 py-1 bg-black text-white rounded">1</span>
              <span className="px-2 py-1">2</span>
              <span className="px-2 py-1">3</span>
              <span className="px-2 py-1">...</span>
            </div>
            <button className="p-2 bg-white rounded-full shadow hover:bg-gray-200">
              <FaArrowRight />
            </button>
          </div>
        </main>
      </div>
    </div>
  );
}