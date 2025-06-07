import React, { useState } from "react";
import { InputField } from "../Components/ui/input-field";
import { Button } from "../Components/ui/button";
import { FaCheck, FaLock, FaEye, FaEyeSlash } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import TopbarDefault from "../Components/TopbarDefault";

export default function Register() {
  const [nome, setNome] = useState("");
  const [sobrenome, setSobrenome] = useState("");
  const [usuario, setUsuario] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false); // NOVO
  const [mostrarConfirmarSenha, setMostrarConfirmarSenha] = useState(false); // NOVO
  const [erro, setErro] = useState("");
  const [erroSenha, setErroSenha] = useState("");
  const [erroEmail, setErroEmail] = useState("");
  const [sucesso, setSucesso] = useState("");
  const navigate = useNavigate();

  const hasMinLength = senha.length >= 8;
  const hasMaxLength = senha.length <= 128;
  const hasUpperLower = /[A-Z]/.test(senha) && /[a-z]/.test(senha);
  const hasNumberSpecial = /[0-9]/.test(senha) && /[^A-Za-z0-9]/.test(senha);
  const hasNoSpaces = !/\s/.test(senha);
  const hasOnlyASCII = [...senha].every((c) => c.charCodeAt(0) < 128);
  const passwordsMatch = senha === confirmarSenha && confirmarSenha !== "";
  const emailValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  const isPasswordValid =
    hasMinLength &&
    hasMaxLength &&
    hasUpperLower &&
    hasNumberSpecial &&
    hasNoSpaces &&
    hasOnlyASCII;

  const isFormValid =
    nome.trim() &&
    sobrenome.trim() &&
    usuario.trim() &&
    emailValido &&
    senha &&
    confirmarSenha &&
    isPasswordValid &&
    passwordsMatch;

  const handleCadastro = () => {
    if (!emailValido) {
      setErroEmail("Digite um email válido.");
      return;
    } else {
      setErroEmail("");
    }

    if (!isPasswordValid || !passwordsMatch) {
      setErroSenha("Corrija os erros da senha antes de continuar.");
      return;
    } else setErroSenha("");

    if (!nome || !sobrenome || !usuario || !email || !senha || !confirmarSenha) {
      setErro("Preencha todos os campos.");
      return;
    }

    if (senha !== confirmarSenha) {
      setErro("As senhas não coincidem.");
      return;
    }

    setErro("");
    setErroSenha("");
    console.log("Cadastro:", { nome, sobrenome, usuario, email, senha });

    setSucesso("Cadastro realizado com sucesso!");
    setTimeout(() => {
      setSucesso("");
      navigate("/dashboard");
    }, 3000);
  };

  return (
    <div className="flex flex-col min-h-screen">
      <TopbarDefault />
      <main className="flex-1 bg-gray-100 flex items-center justify-center px-4 py-6">
        <div className="bg-white rounded-3xl shadow-lg w-full max-w-md p-6 sm:p-8">
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
              placeholder="Sobrenome"
              icon="user"
              value={sobrenome}
              onChange={(e) => setSobrenome(e.target.value)}
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
                const value = e.target.value;
                setEmail(value);
                if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
                  setErroEmail("Digite um email válido.");
                } else {
                  setErroEmail("");
                }
              }}
            />
            {erroEmail && <p className="text-red-500 text-xs -mt-2">{erroEmail}</p>}

            {/* Campo senha com botão de mostrar/ocultar */}
            <div className="relative">
              <InputField
                type={mostrarSenha ? "text" : "password"}
                placeholder="Senha"
                icon="lock"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
              />
              <button
                type="button"
                className="absolute top-4 right-3 text-gray-600"
                onClick={() => setMostrarSenha((prev) => !prev)}
              >
                {mostrarSenha ? <FaEye /> : <FaEyeSlash />}
              </button>
            </div>

            {senha && (
              <div className="text-sm mt-1 space-y-1">
                <p className={hasMinLength ? "text-green-600" : "text-gray-500"}>
                  <FaCheck className="inline mr-1" /> Mínimo 8 caracteres
                </p>
                <p className={hasMaxLength ? "text-green-600" : "text-gray-500"}>
                  <FaCheck className="inline mr-1" /> Máximo 128 caracteres
                </p>
                <p className={hasUpperLower ? "text-green-600" : "text-gray-500"}>
                  <FaCheck className="inline mr-1" /> Letras maiúsculas e minúsculas
                </p>
                <p className={hasNumberSpecial ? "text-green-600" : "text-gray-500"}>
                  <FaCheck className="inline mr-1" /> Números e caractere especial
                </p>
                <p className={hasNoSpaces ? "text-green-600" : "text-gray-500"}>
                  <FaCheck className="inline mr-1" /> Sem espaços
                </p>
                <p className={hasOnlyASCII ? "text-green-600" : "text-gray-500"}>
                  <FaCheck className="inline mr-1" /> Apenas caracteres válidos
                </p>
              </div>
            )}

            {/* Campo confirmar senha com botão de mostrar/ocultar */}
            <div className="relative">
              <InputField
                type={mostrarConfirmarSenha ? "text" : "password"}
                placeholder="Confirmar senha"
                icon="lock"
                value={confirmarSenha}
                onChange={(e) => setConfirmarSenha(e.target.value)}
              />
              <button
                type="button"
                className="absolute top-4 right-3 text-gray-600"
                onClick={() => setMostrarConfirmarSenha((prev) => !prev)}
              >
                {mostrarConfirmarSenha ? <FaEye /> : <FaEyeSlash />}
              </button>
            </div>

            {confirmarSenha && !passwordsMatch && (
              <p className="text-red-500 text-xs -mt-2">As senhas não coincidem</p>
            )}
            {erroSenha && <p className="text-red-500 text-sm text-center">{erroSenha}</p>}
            {erro && <p className="text-red-500 text-sm text-center">{erro}</p>}
            {sucesso && <p className="text-green-600 text-sm text-center">{sucesso}</p>}

            <div className="relative group">
              <Button
                onClick={handleCadastro}
                type="submit"
                className={`w-full transition-all ${
                  isFormValid
                    ? "bg-black hover:bg-gray-700 text-white"
                    : "bg-gray-300 text-gray-500 cursor-not-allowed"
                }`}
                disabled={!isFormValid}
              >
                Finalizar Cadastro
              </Button>

              {!isFormValid && (
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <FaLock className="text-gray-600 text-lg" />
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
