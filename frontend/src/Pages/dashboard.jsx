import React from "react";
import Topbar from "../Components/Topbar";
import Sidebar from "../Components/Sidebar";
export default function Dashboard(){
    return(
        <div className="flex h-screen flex-col">
                <TopbarDefault />
            <div className="flex h-screen">
              <Sidebar />
                <main className="flex-1 bg-gray-100 p-6">
                  <h1>
                    Essa é a Dashboard
                  </h1>
                </main>
              </div>
            </div>
    );
}