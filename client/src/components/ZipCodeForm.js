import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const ZipCodeForm = () => {
  const [zip, setZip] = useState("");
  const [role, setRole] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:5000/api/policies", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ zip: zip.trim(), role }),
      });

      if (!response.ok) {
        throw new Error("Bad response from server");
      }

      const data = await response.json();
      console.log("Policy data:", data);
      navigate("/policies", { state: data });
    } catch (err) {
      console.error("Fetch error:", err);
      alert("Failed to connect to the server. Please make sure the Flask API is running.");
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-md max-w-md w-full">
      <form onSubmit={handleSubmit} className="space-y-4">
        <input
          type="text"
          value={zip}
          onChange={(e) => setZip(e.target.value)}
          placeholder="Enter your ZIP code"
          className="w-full px-4 py-3 border border-blue-200 rounded-lg focus:ring-red-500 focus:outline-none"
          required
        />

        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="w-full px-4 py-3 border border-blue-200 rounded-lg focus:ring-red-500 focus:outline-none"
          required
        >
          <option value="">Select your role</option>
          <option value="student">Student</option>
          <option value="parent">Parent</option>
          <option value="veteran">Veteran</option>
          <option value="worker">Worker</option>
        </select>

        <button
          type="submit"
          className="w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded-lg shadow-md transition-transform hover:scale-105"
        >
          Discover My Policies
        </button>
      </form>
    </div>
  );
};

export default ZipCodeForm;
