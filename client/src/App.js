import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import PolicyHub from "./pages/PolicyHub";
import CongressionalHub from "./pages/CongressionalHub";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer"; // 👈 you'll add this file
import ChatbotWidget from "./components/ChatbotWidget";

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen">
        <Navbar />

        {/* Main content takes up the rest of the height */}
        <div className="flex-grow">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/policies" element={<PolicyHub />} />
            <Route path="/representatives" element={<CongressionalHub />} />
          </Routes>
        </div>

        <Footer />     
        <ChatbotWidget /> 
      </div>
    </Router>
  );
}

export default App;
