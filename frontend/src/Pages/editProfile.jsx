import { useState, useEffect} from "react";
import { FaAddressCard, FaIdBadge, FaUser, FaEnvelope, FaLock, FaPen } from "react-icons/fa";
import TopbarNoSearch from "../Components/TopbarNoSearch";
import { Link, useNavigate } from "react-router-dom";
import { fetchWithAuth } from "../Utils/fetchWithAuth";

export default function EditProfile() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [description, setDescription] = useState("");
  const [profileImage, setProfileImage] = useState(null);

  const navigate = useNavigate();

  useEffect (() =>{
    async function fetchUserData() {
      try {
        const response = await fetchWithAuth(`${process.env.REACT_APP_API_URL}/api/v1/users/me`
        );
       

        if (!response.ok) 
          throw new Error("Erro ao buscar perfil");
        

        const data = await response.json();

        console.log("Resposta perfil: ", data);
        
        setFirstName(data.first_name);
        setLastName(data.last_name);
        setUsername(data.username);
        setEmail(data.email);
        setDescription(data.description || ""); 
      } catch (error) {
        console.error(error);
      }
    }
    fetchUserData();

  }, [])


  const isFormValid =
    firstName.trim() !== "" && lastName.trim() !== "" && username.trim() !== "";

  const handleDB = () => {
    navigate("/dashboard");
  };

  const handleSave = async () => {
    if (!isFormValid) return;
    try {
    const response = await fetchWithAuth(`${process.env.REACT_APP_API_URL}/api/v1/users/me`, 
      {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        username: username,
        description: description
      }),
    });

    if (!response.ok) throw new Error("Erro ao atualizar perfil");

    // Feedback ao usuário (opcional: toast, alerta, etc.)
    alert("Perfil atualizado com sucesso!");

    // Navegar para visualizar perfil
    navigate("/profileView");

  } catch (error) {
    console.error("Erro ao salvar perfil:", error);
    alert("Erro ao salvar perfil.");
  }
};
  

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setProfileImage(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };


  return (
    <div className="flex flex-col h-screen">
      <TopbarNoSearch />
      <div className="flex items-center justify-center h-full overflow-y-auto bg-gradient-to-r from-white to-gray-100">
        {/* Box geral */}
        <div className="max-w-4xl mx-auto w-full h-auto bg-white border border-gray-300 rounded-xl shadow-md p-8 flex flex-col gap-8">
          <h2 className="w-full h-0.5 text-3xl font-bold mb-6 text-center">
            Informações da conta:
          </h2>

          {/* Conteúdo dividido em dois lados */}
          <div className="flex flex-col md:flex-row gap-20">
            {/* Lado Esquerdo */}
            <div className="flex flex-col items-center md:w-1/3">
            
              <div className="w-40 h-40 rounded-full bg-gray-300 relative flex items-center justify-center">
                {profileImage ? (
                  <img
                    src={profileImage}
                    alt="Foto de perfil"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <FaUser className="text-gray-500 text-6xl" />
                )}

                <input
                  type="file"
                  accept="image/*"
                  id="profile-upload"
                  className="hidden"
                  onChange={handleImageChange}
                />

                <label
                  htmlFor="profile-upload"
                  className="absolute -bottom-1 right-10 bg-gray-200 px-3 py-1 rounded-full border flex items-center gap-1 shadow hover:bg-gray-100 cursor-pointer text-black text-sm"
                >
                  <FaPen className="text-sm" />
                  Editar
                </label>
              </div>

              <div className="py-6 w-full">
                <label
                  htmlFor="descricao"
                  className="text-sm text-gray-500 mb-px block"
                >
                  Descrição
                </label>
                <textarea
                className="w-full border rounded-xl p-3 resize-none min-h-[100px]"
                placeholder="+ Descrição"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
              </div>
            </div>

            {/* Lado Direito */}
            <div className="flex-1">
              <div className="flex flex-col">
                {/* Nome */}
                <label
                  htmlFor="fullName"
                  className="text-sm text-gray-500 mb-px"
                >
                  Nome
                </label>
                <div className="relative mb-4">
                  
                  <FaUser className="absolute left-3 top-3 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Nome"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border rounded-full text-black"
                  />
                </div>
                
                {/* Sobrenome */}
                <label
                  htmlFor="fullName"
                  className="text-sm text-gray-500 mb-px"
                >
                  Sobrenome
                </label>
                <div className="relative mb-4 ">
                  <FaAddressCard className="absolute left-3 top-3 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Sobrenome"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border rounded-full"
                  />
                </div>

                {/* Username */}
                <label
                  htmlFor="fullName"
                  className="text-sm text-gray-500 mb-px"
                >
                  Usuário
                </label>
                <div className="relative mb-4 ">
                  <FaIdBadge className="absolute left-3 top-3 text-gray-500" />
                  <input
                    type="text"
                    placeholder="Usuário"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border rounded-full"
                  />
                </div>

                {/* Email */}
                <label
                  htmlFor="fullName"
                  className="text-sm text-gray-500 mb-px"
                >
                  Email
                </label>

                <div className="relative mb-4 opacity-60">
                  <FaEnvelope className="absolute left-3 top-3 text-gray-500" />
                  <input
                    type="email"
                    value={email}
                    disabled
                    className="w-full pl-10 pr-4 py-2 border rounded-full bg-gray-200 cursor-not-allowed "
                  />
                </div>
              </div>

              {/* Botões */}
              <div className="flex gap-3 mt-2 justify-center">
                <button
                  onClick={handleSave}
                  className={`px-6 py-2 rounded-full w-32 text-white transition-colors ${
                    isFormValid
                      ? "bg-black hover:bg-gray-800"
                      : "bg-gray-400 cursor-not-allowed"
                  }`}
                >
                  Salvar
                </button>
                <button
                  onClick={handleDB}
                  className="bg-black text-white px-6 py-2 rounded-full hover:bg-gray-800 w-32"
                >
                  Cancelar
                </button>
              </div>

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
