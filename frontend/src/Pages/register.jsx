import React, { useState } from "react";
import { InputField } from "../Components/ui/input-field";
import { Button } from "../Components/ui/button";
import TopbarNoSearch from "../Components/TopbarNoSearch";
import { FaCheck } from "react-icons/fa";
import { useNavigate } from "react-router-dom";


export default function Register() {
  const [nome, setNome] = useState("");
  const [usuario, setUsuario] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");
  const [erro, setErro] = useState("");
  const [erroSenha, setErroSenha] = useState("");
  const [erroEmail, setErroEmail] = useState("");
  const navigate = useNavigate();


  // Validações
  const hasMinLength = senha.length >= 8;
  const hasMaxLength = senha.length <= 128;
  const hasUpperLower = /[A-Z]/.test(senha) && /[a-z]/.test(senha);
  const hasNumberSpecial = /[0-9]/.test(senha) && /[^A-Za-z0-9]/.test(senha);
  const hasNoSpaces = !/\s/.test(senha);
  const hasOnlyASCII = [...senha].every((c) => c.charCodeAt(0) < 128);
  const passwordsMatch = senha === confirmarSenha && confirmarSenha !== "";

  const isPasswordValid =
    hasMinLength &&
    hasMaxLength &&
    hasUpperLower &&
    hasNumberSpecial &&
    hasNoSpaces &&
    hasOnlyASCII;

  const handleCadastro = () => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setErroEmail("Digite um email válido.");
      return;
    } else {
      setErroEmail("");
    }

    if (!isPasswordValid || !passwordsMatch) {
      setErroSenha("Corrija os erros da senha antes de continuar.");
      return;
    } else setErroSenha("");

    if (!nome || !usuario || !email || !senha || !confirmarSenha) {
      setErro("Preencha todos os campos.");
      return;
    }

    // Verificação extra: senha e confirmação devem bater
    if (senha !== confirmarSenha) {
      setErro("As senhas não coincidem.");
      return;
    }
    setErro("");
    setErroSenha("");
    console.log("Cadastro:", { nome, usuario, email, senha, confirmarSenha });
    navigate("/dashboard");
  };

  return (
    <div className="flex flex-col min-h-screen">
      <TopbarNoSearch />

      <main className="flex-1 bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-lg p-8 w-full max-w-md">
          <h1 className="text-xl font-bold text-center mb-5">Cadastre-se</h1>
          <div className="space-y-4">
            <InputField
              type="text"
              placeholder="Nome"
              icon="user"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
            />

            <InputField
              type="text"
              placeholder="Usuário"
              icon="user"
              value={usuario}
              onChange={(e) => setUsuario(e.target.value)}
            />

            <InputField
              type="email"
              placeholder="Email"
              icon="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                setErroEmail(""); 
              }}
            />
            {erroEmail && (
              <p className="text-red-500 text-xs -mt-2">{erroEmail}</p>
            )}

            <InputField
              type="password"
              placeholder="Senha"
              icon="lock"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
            />

            {/* Regras de senha */}
            {senha && (
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

            <InputField
              type="password"
              placeholder="Confirmar senha"
              icon="lock"
              value={confirmarSenha}
              onChange={(e) => setConfirmarSenha(e.target.value)}
            />

            {/* Aviso se senhas não coincidirem */}
            {confirmarSenha && !passwordsMatch && (
              <p className="text-red-500 text-xs -mt-2">
                As senhas não coincidem
              </p>
            )}

            {erroSenha && (
              <p className="text-red-500 text-sm text-center">{erroSenha}</p>
            )}

            {erro && <p className="text-red-500 text-sm text-center">{erro}</p>}

            <Button onClick={handleCadastro} type="submit">
              Finalizar Cadastro
            </Button>
          </div>
        </div>
      </main>
    </div>
  );
}
