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

// Importe o componente FileViewer
import { FileViewer } from "../Components/file-viewer";

// Mock de arquivos - ATUALIZADO com URLs de exemplo realistas e 'descricao'
const mockArquivos = [
  {
    id: "1",
    title: "Product Demo Video", 
    type: "video", 
    url: "https://www.learningcontainer.com/wp-content/uploads/2020/05/sample-mp4-file.mp4",
    thumbnail: "https://via.placeholder.com/150x100?text=Video+Thumb", 
    
    size: "45.2 MB", 
    uploadDate: "14/01/2024",
    duration: "3:24", 
    genre: "Educational", 
    description: "Comprehensive product demonstration showcasing key features",
    tags: ["demo", "product", "education"], 
    resolution: "1920x1080", 
    format: "MP4", 
  },
 {
    id: "2",
    title: "Product Demo Video", 
    type: "image", 
    url: "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png",
    thumbnailUrl: "https://via.placeholder.com/150x100?text=Logo+Thumb", 
    size: "45.2 MB", 
    uploadDate: "14/01/2024", 
    genre: "Educational", 
    description: "Comprehensive product demonstration showcasing key features",
    tags: ["demo", "product", "education"],
    resolution: "1920x1080", 
    format: "IMG", 
  }
  
];

// Componente de visualização dos arquivos
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
            alt={file.nome}
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

        {(file.type === "video" || file.type === "audio") && file.duracao && (
          <div className="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white text-xs px-2 py-1 rounded">
            {file.duracao}
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
  const [selectedFile, setSelectedFile] = useState(null); // Estado para controlar o modal

  useEffect(() => {
    // Simula o carregamento dos arquivos
    setTimeout(() => {
      setArquivos(mockArquivos);
    }, 500);
  }, []);

  // Função para lidar com o clique no FileCard
  const handleFileCardClick = (file) => {
    setSelectedFile(file);
  };

  // Função para fechar o modal
  const handleCloseFileViewer = () => {
    setSelectedFile(null);
  };

  return (
    <div className="flex flex-col h-screen">
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
      <div className="flex flex-1 overflow-hidden">
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
                  <FileCard
                    key={file.id}
                    file={file}
                    onClick={handleFileCardClick} // Passa a função de clique
                  />
                ))}
              </div>
            )}
          </div>

          {/* 
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
          Paginação */}
        </main>
      </div>

      {/* Renderiza o FileViewer se houver um arquivo selecionado */}
      {selectedFile && (
        <FileViewer file={selectedFile} onClose={handleCloseFileViewer} />
      )}
    </div>
  );
}