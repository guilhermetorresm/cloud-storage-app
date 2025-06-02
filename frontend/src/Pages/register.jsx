import React, { useState } from "react";
import { InputField } from "../Components/ui/input-field";
import { Button } from "../Components/ui/button";
import TopbarNoSearch from "../Components/TopbarNoSearch";

export default function Register() {
  const [nome, setNome] = useState("");
  const [usuario, setUsuario] = useState("");
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");

  const handleCadastro = () => {
    console.log("Cadastro:", { nome, usuario, email, senha, confirmarSenha });
  };

  return (
    <div className="flex flex-col min-h-screen">
      <TopbarNoSearch />
      
        <main className="flex-1 bg-gray-100 flex items-center justify-center p-4">
            <div className="bg-white rounded-3xl shadow-lg p-8 w-full max-w-md">
              <h1 className="text-xl font-bold text-center  mb-5"> Cadastre-se </h1>
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
                  type="text"
                  placeholder="Email"
                  icon="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />

                <InputField
                  type="password"
                  placeholder="Senha"
                  icon="lock"
                  value={senha}
                  onChange={(e) => setSenha(e.target.value)}
                />

                <InputField
                  type="password"
                  placeholder="Confirmar senha"
                  icon="lock"
                  value={confirmarSenha}
                  onChange={(e) => setConfirmarSenha(e.target.value)}
                />

                <Button onClick={handleCadastro} type="submit">
                  Finalizar Cadastro
                </Button>
              </div>
            </div>

        </main>
    
    </div>
  );
}
