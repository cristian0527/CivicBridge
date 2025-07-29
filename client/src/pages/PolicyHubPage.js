import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const PolicyHubPage = () => {
  const [zip, setZip] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (zip.length !== 5 || isNaN(zip)) {
      setError("Please enter a valid 5-digit ZIP code.");
      return;
    }
    setError("");
    navigate("/policies", { state: { zip } });
  };

  return (
    <div className="p-6 max-w-4xl mx-auto text-center">
      <h2 className="text-3xl font-extrabold text-blue-900 mb-4">
        Explore National Policies
      </h2>
      <p className="text-gray-700 mb-6 max-w-xl mx-auto">
        Curious about recent laws or regulations? Enter your ZIP code below to browse
        federal policies that may affect your community.
      </p>
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row justify-center items-center gap-4">
        <input
          type="text"
          value={zip}
          onChange={(e) => setZip(e.target.value)}
          placeholder="ZIP code"
          className="border border-gray-300 rounded-md px-4 py-2 w-48 focus:ring-2 focus:ring-blue-900 focus:outline-none"
          required
        />
        <button
          type="submit"
          className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded shadow transition"
        >
          View Policies
        </button>
      </form>
      {error && <p className="text-red-500 mt-3">{error}</p>}
    </div>
  );
};

export default PolicyHubPage;
