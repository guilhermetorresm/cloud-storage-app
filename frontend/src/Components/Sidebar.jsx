// Sidebar.jsx
import { Upload, Trash2, LogOut } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Sidebar() {
  const navigate = useNavigate();

  const handleExit = () => {
    console.log("Clicou em sair");
    navigate("/");
  };

  return (
    <aside className="w-60 h-full bg-white border-r shadow-sm flex flex-col p-4 overflow-hidden">
      {/* Conteúdo principal */}
      <div>
        <nav className="space-y-4">
          <button className="flex items-center space-x-2 text-left hover:text-blue-600">
            <Upload className="w-5 h-5" />
            <span>Upload</span>
          </button>
          <button className="flex items-center space-x-2 text-left hover:text-red-600">
            <Trash2 className="w-5 h-5" />
            <span>Lixeira</span>
          </button>
        </nav>
      </div>

      <div className="mt-auto">
        <hr className="my-4 border-gray-300" />
        <button
          onClick={handleExit}
          className="z-10 text-red-600 font-semibold flex items-center space-x-2 hover:underline w-full"
        >
          <LogOut />
          <span>Sair</span>
        </button>
      </div>
    </aside>
  );
}
