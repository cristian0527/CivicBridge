import React, { useState } from "react";
import OfficialCard from "../components/OfficialCard";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const CongressionalHub = () => {
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
    <div className="p-6 max-w-6xl mx-auto">
      <div className="text-center">
        <h2 className="text-3xl font-extrabold text-blue-900 mb-4">
          Find Your Elected Officials
        </h2>
        <p className="text-gray-700 mb-6 max-w-2xl mx-auto">
          Enter your ZIP code to see who represents you in Congress and how to reach them.
        </p>

        <div className="flex flex-col sm:flex-row justify-center items-center gap-4 mb-6">
          <input
            type="text"
            placeholder="ZIP code"
            value={zip}
            onChange={(e) => setZip(e.target.value)}
            className="border border-gray-300 rounded-md px-4 py-2 w-48 focus:ring-2 focus:ring-blue-900 focus:outline-none"
          />
          <button
            onClick={fetchOfficials}
            className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded shadow transition"
          >
            Search
          </button>
        </div>

        {error && <p className="text-red-500 mb-4">{error}</p>}
        {loading && <p className="text-gray-500 mb-4">Loading officials...</p>}
      </div>

      {officials.length > 0 && (
        <div className="grid gap-6 sm:grid-cols-2 md:grid-cols-3 items-start text-left">
          {officials.map((rep, i) => (
            <div key={i} className="flex justify-center">
              <OfficialCard rep={rep} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CongressionalHub;
