"use client";

import { useState } from "react";
import { InputField } from "../Components/ui/input-field";
import { Button } from "../Components/ui/button";
import { useNavigate } from "react-router-dom";
import logo from "../Assets/logo_cortada.png";
import { login } from "../Services/auth";
import { Notification } from "../Components/ui/notification";

export default function LoginScreen() {
  const [usuario, setUsuario] = useState("");
  const [senha, setSenha] = useState("");
  const navigate = useNavigate();
  const [statusMsg, setStatusMsg] = useState("");
  const [statusMsgType, setStatusMsgType] = useState("error");

  const isFormValid = usuario.trim() !== "" && senha.trim() !== "";

  const handleLogin = async () => {
    try {
      const response = await login(usuario, senha);
      const { access_token } = response.data;

      localStorage.setItem("token", access_token);

      setStatusMsg("");
      setStatusMsgType("success");
      setStatusMsg("Login realizado com sucesso!");
      setTimeout(() => navigate("/dashboard"), 1500);
    } catch (error) {
      setStatusMsgType("error");
      const message =
        error?.response?.data?.detail || "Usário ou senha inválidos.";
      setStatusMsg(message);
    }
  };

  const handleRegister = () => {
    console.log("Cadastrar-se");
    navigate("/register");
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      {statusMsg && (
        <Notification
        key={statusMsg + statusMsgType}
          message={statusMsg}
          type={statusMsgType}
          onClose={() => setStatusMsg("")}
        />
      )}
      <div className="bg-white rounded-3xl shadow-lg p-6 sm:p-8 w-full max-w-md">
        <div className="flex justify-center mb-5">
          <img src={logo} alt="Logo" className="h-10 w-auto max-w-full" />
        </div>

        <div className="space-y-4">
          <InputField
            type="text"
            placeholder="Usuário"
            icon="user"
            value={usuario}
            onChange={(e) => setUsuario(e.target.value)}
          />

          <InputField
            type="password"
            placeholder="Senha"
            icon="lock"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
          />

          <div className="text-right">
            <button className="text-sm text-gray-500 hover:text-gray-700">
              Esqueceu a senha?
            </button>
          </div>

          <Button
            onClick={handleLogin}
            type="submit"
            className="w-full"
            disabled={!isFormValid}
          >
            Entrar
          </Button>

          <div className="text-center text-gray-500 text-sm">OU</div>

          <Button
            onClick={handleRegister}
            variant="secondary"
            className="w-full"
          >
            Cadastrar-se
          </Button>
        </div>
      </div>
    </div>
  );
}
