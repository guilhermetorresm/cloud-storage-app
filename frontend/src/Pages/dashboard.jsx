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
} from "react-icons/fa";

// Mock de arquivos
const mockArquivos = [
  {
    id: "1",
    nome: "Coração.png",
    tipo: "image",
    url: "https://via.placeholder.com/100x100.png?text=Img1",
  },
  { id: "2", nome: "Áudio.mp3", tipo: "audio" },
  { id: "3", nome: "Vídeo.mp4", tipo: "video" },
  { id: "4", nome: "Documento.PDF", tipo: "pdf" },
  { id: "5", nome: "Texto.txt", tipo: "text" },
  { id: "6", nome: "Arquivos.zip", tipo: "zip" },
];

// Componente de visualização dos arquivos
const FileCard = ({ file }) => {
  let icon;

  if (file.tipo === "image") {
    return (
      <div className="bg-white rounded-xl shadow p-3 flex flex-col items-center">
        <img
          src={file.url}
          alt={file.nome}
          className="w-20 h-20 object-cover rounded"
        />
        <p className="text-sm mt-2 truncate text-center">{file.nome}</p>
      </div>
    );
  }

  switch (file.tipo) {
    case "audio":
      icon = <FaFileAudio size={50} className="text-indigo-500" />;
      break;
    case "video":
      icon = <FaFileVideo size={50} className="text-red-500" />;
      break;
    case "pdf":
      icon = <FaFilePdf size={50} className="text-blue-600" />;
      break;
    case "text":
      icon = <FaFileAlt size={50} className="text-green-600" />;
      break;
    case "zip":
      icon = <FaFileArchive size={50} className="text-black" />;
      break;
    default:
      icon = <FaFileAlt size={50} />;
  }

  return (
    <div className="bg-white rounded-xl shadow p-3 flex flex-col items-center text-center">
      {icon}
      <p className="text-sm mt-2 truncate">{file.nome}</p>
    </div>
  );
};

export default function Dashboard() {
  const [arquivos, setArquivos] = useState([]);
  const [menuAberto, setMenuAberto] = useState(false);

  useEffect(() => {
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

          {/* Paginação */}
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
