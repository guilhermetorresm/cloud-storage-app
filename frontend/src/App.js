// src/App.js
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import EditProfile from "./Pages/editProfile";
import EditPassword from "./Pages/editPassword";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<EditProfile />} />
        <Route path="/editPassword" element={<EditPassword />} />
      </Routes>
    </Router>
  );
}

export default App;