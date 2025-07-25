import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const ZipCodeForm = () => {
  const [zip, setZip] = useState("");
  const [role, setRole] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    navigate("/policies", { state: { zip, role } });
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
