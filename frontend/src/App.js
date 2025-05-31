import Sidebar from "./Components/Sidebar";
// import Topbar from "./Components/Topbar";
//import TopbarNoSearch from "./Components/TopbarNoSearch";
import TopbarDefault from "./Components/TopbarDefault";

export default function App() {
  return (
      <div className="flex h-screen flex-col">
        <TopbarDefault />
    <div className="flex h-screen">
      <Sidebar />
        <main className="flex-1 bg-gray-100 p-6">
          {/* Aqui vai o conteúdo central */}
        </main>
      </div>
    </div>
  );
}
