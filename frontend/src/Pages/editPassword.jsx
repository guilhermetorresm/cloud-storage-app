import { useState } from "react";
import { FaLock, FaCheck, FaEye, FaEyeSlash } from "react-icons/fa";
import TopbarNoSearch from "../Components/TopbarNoSearch";
import { Link } from "react-router-dom";

export default function EditPassword() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const hasMinLength = newPassword.length >= 8;
  const hasMaxLength = newPassword.length <= 128;
  const hasUpperLower = /[A-Z]/.test(newPassword) && /[a-z]/.test(newPassword);
  const hasNumberSpecial = /[0-9]/.test(newPassword) && /[^A-Za-z0-9]/.test(newPassword);
  const hasNoSpaces = !/\s/.test(newPassword);
  const hasOnlyASCII = [...newPassword].every(c => c.charCodeAt(0) < 128);
  const passwordsMatch = newPassword === confirmPassword && confirmPassword !== "";

  return (
    <div className="flex flex-col min-h-screen">
      <TopbarNoSearch />

      <div className="flex-1 flex items-center justify-center bg-gray-50 p-4">
        <div className="bg-white rounded-lg shadow-md p-8 w-full max-w-md">
          <h1 className="text-2xl font-bold text-center mb-2">Alterar senha</h1>

          <div className="space-y-6">
            {/* Senha atual */}
            <div>
              <h2 className="font-medium mb-3">Senha atual</h2>
              <div className="relative">
                <FaLock className="absolute left-3 top-3 text-gray-500" />
                <input
                  type={showCurrentPassword ? "text" : "password"}
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
                />
                <button
                  type="button"
                  className="absolute right-3 top-3 text-gray-500 hover:text-gray-700"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                >
                  {showCurrentPassword ? <FaEye /> : <FaEyeSlash />}
                </button>
              </div>
            </div>

            {/* Nova senha */}
            <div>
              <h2 className="font-medium mb-3">Nova senha</h2>
              <div className="relative">
                <FaLock className="absolute left-3 top-3 text-gray-500" />
                <input
                  type={showNewPassword ? "text" : "password"}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full pl-10 pr-10 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-black"
                />
                <button
                  type="button"
                  className="absolute right-3 top-3 text-gray-500 hover:text-gray-700"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                >
                  {showNewPassword ? <FaEye /> : <FaEyeSlash />}
                </button>
              </div>
            </div> 
            {/* Regras de senha */}
                        {newPassword && (
                          <div className="text-sm mt-1 space-y-1">
                            <p
                              className={`${
                                hasMinLength ? "text-green-600" : "text-gray-500"
                              }`}
                            >
                              <FaCheck className="inline mr-1" />
                              Mínimo 8 caracteres
                            </p>            
                            <p
                              className={`${
                                hasMaxLength ? "text-green-600" : "text-gray-500"
                              }`}
                            >
                              <FaCheck className="inline mr-1" />
                              Máximo 128 caracteres
                            </p>
                            <p
                              className={`${
                                hasUpperLower ? "text-green-600" : "text-gray-500"
                              }`}
                            >
                              <FaCheck className="inline mr-1" />
                              Letras maiúsculas e minúsculas
                            </p>
                            <p
                              className={`${
                                hasNumberSpecial ? "text-green-600" : "text-gray-500"
                              }`}
                            >
                              <FaCheck className="inline mr-1" />
                              Números e caractere especial
                            </p>
                            <p
                              className={`${
                                hasNoSpaces ? "text-green-600" : "text-gray-500"
                              }`}
                            >
                              <FaCheck className="inline mr-1" />
                              Sem espaços
                            </p>
                            <p
                              className={`${
                                hasOnlyASCII ? "text-green-600" : "text-gray-500"
                              }`}
                            >
                              <FaCheck className="inline mr-1" />
                              Apenas caracteres válidos (sem Unicode)
                            </p>
                          </div>
                        )}

            {/* Confirmar nova senha */}
            <div>
              <h2 className="font-medium mb-3">Confirmar nova senha</h2>
              <div className="relative">
                <FaLock className="absolute left-3 top-3 text-gray-500" />
                <input
                  type={showConfirmPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className={`w-full pl-10 pr-10 py-2 border rounded-lg focus:outline-none focus:ring-2 ${
                    confirmPassword ? (passwordsMatch ? 'focus:ring-green-500' : 'focus:ring-red-500') : 'focus:ring-black'
                  }`}
                />
                <button
                  type="button"
                  className="absolute right-3 top-3 text-gray-500 hover:text-gray-700"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                >
                  {showConfirmPassword ? <FaEye /> : <FaEyeSlash />}
                </button>
              </div>
              {confirmPassword && !passwordsMatch && (
                <p className="text-red-500 text-xs mt-1">As senhas não coincidem</p>
              )}
            </div>

            {/* Botão de submit */}
            <button
              className={`w-full py-2 rounded-lg transition-colors font-medium ${
                hasMinLength &&
                hasUpperLower &&
                hasNumberSpecial &&
                hasNoSpaces &&
                hasOnlyASCII &&
                passwordsMatch &&
                currentPassword
                  ? 'bg-black text-white hover:bg-gray-800'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
              disabled={
                !hasMinLength ||
                !hasUpperLower ||
                !hasNumberSpecial ||
                !hasNoSpaces ||
                !hasOnlyASCII ||
                !passwordsMatch ||
                !currentPassword
              }
            >
              Alterar senha
            </button>

            {/* Voltar */}
            <div className="text-center">
              <Link to="/editProfile" className="text-black hover:underline text-sm">
                Voltar à edição de perfil
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
