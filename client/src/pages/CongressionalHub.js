import React, { useState } from "react";
import OfficialCard from "../components/OfficialCard";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const CongressionalHub = () => {
  console.log("🧪 REACT_APP_BACKEND_URL:", BACKEND_URL);
  const [zip, setZip] = useState("");
  const [officials, setOfficials] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchOfficials = async () => {
    if (!zip || zip.length !== 5) {
      setError("Please enter a valid 5-digit ZIP code.");
      return;
    }

    setLoading(true);
    setError("");
    setOfficials([]);

    try {
      console.log("📡 Fetching from:", `${BACKEND_URL}/api/representatives`);
      const res = await fetch(`${BACKEND_URL}/api/representatives`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ zip }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Server error: ${res.status} - ${text}`);
      }

      const data = await res.json();
      setOfficials(data.representatives || []);
    } catch (err) {
      console.error("Fetch error:", err);
      setError("Could not load representatives. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Find Your Elected Officials</h2>

      <div className="flex gap-3 mb-6">
        <input
          type="text"
          placeholder="Enter your ZIP code"
          value={zip}
          onChange={(e) => setZip(e.target.value)}
          className="border rounded px-3 py-2 w-40"
        />
        <button
          onClick={fetchOfficials}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
        >
          Search
        </button>
      </div>

      {error && <p className="text-red-500 mb-4">{error}</p>}
      {loading && <p className="text-gray-500">Loading officials...</p>}

      {officials.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
          {officials.map((rep, i) => (
            <OfficialCard key={i} rep={rep} />
          ))}
        </div>
      )}
    </div>
  );
};

export default CongressionalHub;
