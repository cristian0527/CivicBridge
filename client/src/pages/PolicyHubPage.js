import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const categories = [
  { value: "healthcare", label: "Healthcare" },
  { value: "housing", label: "Housing" },
  { value: "education", label: "Education" },
  { value: "employment", label: "Employment" },
  { value: "taxes", label: "Taxes" },
  { value: "environment", label: "Environment" },
  { value: "transportation", label: "Transportation" },
  { value: "immigration", label: "Immigration" },
  { value: "social_security", label: "Social Security" },
  { value: "veterans", label: "Veterans" }
];

const PolicyHubPage = () => {
  const [topic, setTopic] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!topic) {
      setError("Please select a topic.");
      return;
    }
    setError("");
    navigate("/policies", { state: { topic } });
  };

  return (
    <div className="p-6 max-w-4xl mx-auto text-center">
      <h2 className="text-3xl font-extrabold text-blue-900 mb-4">
        Explore National Policies
      </h2>
      <p className="text-gray-700 mb-6 max-w-xl mx-auto">
        Curious about recent laws or regulations? Choose a topic to browse
        federal and congressional policies that may affect your community.
      </p>
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row justify-center items-center gap-4">
        <select
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          className="border border-gray-300 rounded-md px-4 py-2 w-60 focus:ring-2 focus:ring-blue-900 focus:outline-none"
          required
        >
          <option value="">Select a Topic</option>
          {categories.map((cat) => (
            <option key={cat.value} value={cat.value}>{cat.label}</option>
          ))}
        </select>
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
