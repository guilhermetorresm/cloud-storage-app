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
} from "react-icons/fa";

const mockArquivos = [
  {
    id: "1",
    nome: "Coração.png",
    tipo: "image",
    url: "https://via.placeholder.com/100x100.png?text=Img1",
  },
  {
    id: "2",
    nome: "Áudio.mp3",
    tipo: "audio",
  },
  {
    id: "3",
    nome: "Vídeo.mp4",
    tipo: "video",
  },
  {
    id: "4",
    nome: "Documento.PDF",
    tipo: "pdf",
  },
  {
    id: "5",
    nome: "Texto.txt",
    tipo: "text",
  },
  {
    id: "6",
    nome: "Arquivos.zip",
    tipo: "zip",
  },
];

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

  useEffect(() => {
    // Simulando fetch de dados do backend
    setTimeout(() => {
      setArquivos(mockArquivos);
    }, 500); // Simula carregamento
  }, []);

  return (
    <div className="flex h-screen flex-col">
      <Topbar />
      <div className="flex h-screen">
        <Sidebar />
        <main className="flex-1 bg-gray-100 p-6 flex flex-col">
          <div className="flex-1 overflow-auto">
            <div className="max-w-6xl mx-auto">
              {arquivos.length === 0 ? (
                <p className="text-center">Carregando arquivos...</p>
              ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
                  {arquivos.map((file) => (
                    <FileCard key={file.id} file={file} />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Paginação fictícia */}
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
