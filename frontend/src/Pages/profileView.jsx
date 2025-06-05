// src/Pages/editProfile.js
import { useState } from "react";
import { FaUser, FaEnvelope, FaLock } from "react-icons/fa";
import TopbarNoSearch from "../Components/TopbarNoSearch";
import { Link, useNavigate } from "react-router-dom";

export default function EditProfile() {
  const [fullName, getFullName] = useState("");
  const [username, getUsername] = useState("");
  const [description, getDescription] = useState("");
  const navigate = useNavigate();

  const handleEditarPerfil = () => {
    navigate("/editProfile");
  };

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
                {/* Foto de perfil */}
              </div>
              <div className="w-full">
                <label
                  htmlFor="descricao"
                  className="text-sm text-gray-500 mb-px block"
                >
                  Descrição
                </label>
                <textarea
                  className=" w-full border rounded-xl p-3 resize-none min-h-[100px]"
                  placeholder="+ Descrição"
                  value={description}
                  disabled
                />
              </div>
            </div>

            {/* Lado Direito */}
            <div className="flex-1">
              <div className="flex flex-col">
                {/* Nome Completo */}
                <label
                  htmlFor="fullName"
                  className="text-sm text-gray-500 mb-px"
                >
                  Nome Completo
                </label>
                <div className="relative mb-4 opacity-60">
                  <FaUser className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Nome Completo"
                    value={fullName}
                    disabled
                    className="w-full pl-10 pr-4 py-2 border rounded-full bg-gray-200 cursor-not-allowed"
                  />
                </div>

                {/* Usuário */}
                <label
                  htmlFor="username"
                  className="text-sm text-gray-500 mb-px"
                >
                  Usuário
                </label>
                <div className="relative mb-4 opacity-60">
                  <FaUser className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 " />
                  <input
                    type="text"
                    placeholder="UserName"
                    value={username}
                    disabled
                    className="w-full pl-10 pr-4 py-2 border rounded-full bg-gray-200 cursor-not-allowed"
                  />
                </div>

                {/* Email */}
                <label htmlFor="email" className="text-sm text-gray-500 mb-px">
                  Email
                </label>
                <div className="relative opacity-60">
                  <FaEnvelope className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
                  <input
                    type="email"
                    value="usuario@email.com"
                    disabled
                    className="w-full pl-10 pr-4 py-2 border rounded-full bg-gray-200 cursor-not-allowed"
                  />
                </div>
              </div>

              {/* Botão */}
              <div className="flex gap-4 mt-6 justify-center">
                <button
                  onClick={handleEditarPerfil}
                  className="bg-black text-white px-6 py-2 rounded-full hover:bg-gray-800 w-80"
                >
                  Editar Perfil
                </button>
              </div>
              {/* Link para alterar senha - MODIFICAÇÃO PRINCIPAL */}
              <div className="flex gap-4 mt-6 justify-center">
                <Link
                  to="/editPassword"
                  className="inline-flex items-center justify-center gap-2 px-4 py-2 text-gray-700 hover:text-black hover:bg-gray-100 rounded-full transition-colors w-80"
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
