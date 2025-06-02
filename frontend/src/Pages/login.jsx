"use client";

import { useState } from "react";
import { InputField } from "../Components/ui/input-field";
import { Button } from "../Components/ui/button";
import { useNavigate } from "react-router-dom";
import logo from '../Assets/logo_cortada.png';


export default function LoginScreen() {
  const [usuario, setUsuario] = useState("");
  const [senha, setSenha] = useState("");
  const navigate = useNavigate();


  const handleLogin = () => {
    console.log("Login:", { usuario, senha });
    navigate("/dashboard");
  };

  const handleRegister = () => {
    console.log("Cadastrar-se");
    navigate("/register");
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-3xl shadow-lg p-8 w-full max-w-md">

        <div className="flex justify-center space-x-3 mb-5">
                <img src={logo} alt="Logo" className="h-10 w-25" />
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
              esqueceu a senha?
            </button>
          </div>

          <Button onClick={handleLogin} type="submit">
            Entrar
          </Button>

          <div className="text-center text-gray-500 text-sm">OU</div>

          <Button onClick={handleRegister} variant="secondary">
            Cadastrar-se
          </Button>
        </div>
      </div>
    </div>
  );
}
