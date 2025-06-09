import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginScreen from "./Pages/login";
import Dashboard from "./Pages/dashboard";
import Register from "./Pages/register";
import EditPassword from "./Pages/editPassword";
import EditProfile from "./Pages/editProfile";
import ProfileView from "./Pages/profileView";
import PrivateRoute from "./Components/privateRouter";  // importar o componente criado

export default function App() {
  return (
    <Router>
      <Routes>
        {/* Página de Login e Registro não precisam de autenticação */}
        <Route path="/" element={<LoginScreen />} />
        <Route path="/Register" element={<Register />} />

        {/* Rotas protegidas - só acessa se autenticado */}
        <Route
          path="/DashBoard"
          element={
            <PrivateRoute>
              <Dashboard />
            </PrivateRoute>
          }
        />
        <Route
          path="/EditProfile"
          element={
            <PrivateRoute>
              <EditProfile />
            </PrivateRoute>
          }
        />
        <Route
          path="/EditPassword"
          element={
            <PrivateRoute>
              <EditPassword />
            </PrivateRoute>
          }
        />
        <Route
          path="/ProfileView"
          element={
            <PrivateRoute>
              <ProfileView />
            </PrivateRoute>
          }
        />
      </Routes>
    </Router>
  );
}
