import { Navigate } from "react-router-dom";

function PrivateRoute({ children }) {
  const token = localStorage.getItem("access_token"); // ou outro nome que você usa

  if (!token) {
    // Se não tiver token, redireciona para login
    return <Navigate to="/" replace />;
  }

  // Se tiver token, renderiza o componente protegido
  return children;
}

export default PrivateRoute;
