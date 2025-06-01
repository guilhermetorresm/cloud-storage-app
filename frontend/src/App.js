import {BrowserRouter as Router, Routes, Route} from "react-router-dom";
import LoginScreen from "./Pages/login";
import Dashboard from "./Pages/dashboard";
 export default function App(){
  return(
    <Router>
      <Routes>
        {/*Página de Login */}
        <Route path="/" element={<LoginScreen/>}/>
        
        {/*DashBoard */}
        <Route path="/DashBoard" element={<Dashboard/>}/>

      </Routes>
    </Router>
  );
 }