// Components/FileCard.jsx
import {
  FaFilePdf,
  FaFileAudio,
  FaFileVideo,
  FaFileArchive,
  FaFileAlt,
  FaImage,
} from "react-icons/fa";

const FileCard = ({ file, onClick }) => {
  const getTypeColor = (type) => {
    switch (type) {
      case "video": return "bg-blue-100 text-blue-800";
      case "image": return "bg-green-100 text-green-800";
      case "audio": return "bg-purple-100 text-purple-800";
      case "pdf": return "bg-red-100 text-red-800";
      case "document": return "bg-yellow-100 text-yellow-800";
      case "text": return "bg-yellow-100 text-yellow-800";
      case "zip": return "bg-gray-100 text-gray-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case "video": return <FaFileVideo className="text-blue-500" />;
      case "image": return <FaImage className="text-green-500" />;
      case "audio": return <FaFileAudio className="text-purple-500" />;
      case "pdf": return <FaFilePdf className="text-red-500" />;
      case "document": return <FaFileAlt className="text-yellow-500" />;
      case "text": return <FaFileAlt className="text-yellow-500" />;
      case "zip": return <FaFileArchive className="text-gray-500" />;
      default: return <FaFileAlt className="text-gray-500" />;
    }
  };

  // Lógica para renderizar a thumbnail ou o ícone do tipo de arquivo
  const renderThumbnailOrIcon = (file) => {
    if (file.type === "image" && file.url) {
      return (
        <img
          src={file.url}
          alt={file.title || "Imagem"}
          className="w-full h-full object-cover"
        />
      );
    } else if (file.type === "video" && file.thumbnail_url) {
      return (
        <img
          src={file.thumbnail_url}
          alt={`Thumbnail de ${file.title}`}
          className="w-full h-full object-cover"
        />
      );
    }
    // Para todos os outros casos, ou se não houver URL/thumbnail_url, mostra o ícone padrão
    return <div className="text-5xl text-gray-400">{getTypeIcon(file.type)}</div>;
  };

  return (
    <div
      className="relative bg-white rounded-xl shadow-md overflow-hidden hover:shadow-lg transition-shadow duration-300 cursor-pointer"
      onClick={() => onClick(file)}
    >
      <div className="relative bg-gray-200 w-full flex items-center justify-center aspect-video overflow-hidden">
        {renderThumbnailOrIcon(file)}

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
          {file.size_humanized && <p>{file.size_humanized}</p>}
          {file.uploadDate && <p>{file.uploadDate}</p>}
        </div>
      </div>
    </div>
  );
};

export default FileCard;