import {BrowserRouter as Router, Routes, Route} from "react-router-dom";
import LoginScreen from "./Pages/login";
import Dashboard from "./Pages/dashboard";
import Register from "./Pages/register";
import EditPassword from "./Pages/editPassword";
import EditProfile from "./Pages/editProfile";
 export default function App(){
  return(
    <Router>
      <Routes>
        {/*Página de Login */}
        <Route path="/" element={<LoginScreen/>}/>
        
        {/*DashBoard */}
        <Route path="/DashBoard" element={<Dashboard/>}/>

        {/*Cadastro */}
        <Route path="/Register" element={<Register/>}/>

        {/*Editar Perfil */}
        <Route path="/EditProfile" element={<EditProfile/>}/>

        {/*Editar Senha */}
        <Route path="/EditPassword" element={<EditPassword/>}/>

      </Routes>
    </Router>
  );
 }
