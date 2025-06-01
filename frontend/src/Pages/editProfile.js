// src/Pages/editProfile.js
import { useState } from "react";
import { FaUser, FaEnvelope, FaLock, FaPen } from "react-icons/fa";
import TopbarNoSearch from "../Components/TopbarNoSearch";
import { Link } from "react-router-dom";

export default function EditProfile() {
  const [fullName, setFullName] = useState("");
  const [username, setUsername] = useState("");
  const [description, setDescription] = useState("");

  return (
    <div className="flex flex-col h-screen">
      <TopbarNoSearch />
      <div className="flex items-center justify-center h-full overflow-y-auto bg-gradient-to-r from-white to-gray-100">
        {/* Box geral */}
        <div className="max-w-4xl mx-auto w-full h-auto bg-white border border-gray-300 rounded-xl shadow-md p-8 flex flex-col gap-8">
          {/* Título da box centralizado */}
          <h2 className="w-full h-0.5 text-3xl font-bold mb-6 text-center">
            Informações da conta:
          </h2>

          {/* Conteúdo dividido em dois lados */}
          <div className="flex flex-col md:flex-row gap-20">
            {/* Lado Esquerdo */}
            <div className="flex flex-col items-center md:w-1/3">
              <div className="w-40 h-40 rounded-full bg-gray-300 relative">
                <button className="absolute bottom-2 right-2 transform translate-x-1/2 bg-white px-4 py-1 rounded-full border flex items-center gap-2 shadow hover:bg-gray-100">
                  <FaPen className="text-sm" />
                  Editar
                </button>
              </div>
              <textarea
                className="mt-6 w-full border rounded-xl p-3 resize-none min-h-[100px]"
                placeholder="+ Descrição"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {/* Lado Direito */}
            <div className="flex-1">
              <div className="flex flex-col gap-4">
                <div className="relative">
                  <FaUser className="absolute left-3 top-3 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Nome Completo"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border rounded-full"
                  />
                </div>

                <div className="relative">
                  <FaUser className="absolute left-3 top-3 text-gray-500" />
                  <input
                    type="text"
                    placeholder="UserName"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border rounded-full"
                  />
                </div>

                <div className="relative opacity-60">
                  <FaEnvelope className="absolute left-3 top-3 text-gray-500" />
                  <input
                    type="email"
                    value="usuario@email.com"
                    disabled
                    className="w-full pl-10 pr-4 py-2 border rounded-full bg-gray-200 cursor-not-allowed"
                  />
                </div>
              </div>

              {/* Botões */}
              <div className="flex gap-4 mt-6 justify-center">
                <button className="bg-black text-white px-6 py-2 rounded-full hover:bg-gray-800">Salvar</button>
                <button className="bg-black text-white px-6 py-2 rounded-full hover:bg-gray-800">Cancelar</button>
              </div>

              {/* Link para alterar senha - MODIFICAÇÃO PRINCIPAL */}
              <div className="mt-6 text-center">
                <Link 
                  to="/editPassword"
                  className="inline-flex items-center gap-2 px-4 py-2 text-gray-700 hover:text-black hover:bg-gray-100 rounded-full transition-colors"
                >
                  <FaLock className="text-sm" />
                  <span className="font-medium">Alterar senha</span>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}