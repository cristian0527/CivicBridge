import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PoliciesPage = () => {
  const { state } = useLocation();
  const zip = state?.zip || "";
  const [policies, setPolicies] = useState([]);
  const [search, setSearch] = useState("");
  const [filtered, setFiltered] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!zip) return;
    fetch(`${BACKEND_URL}/api/policyhub?zip=${zip}`)
      .then((res) => res.json())
      .then((data) => setPolicies(data.policies || []))
      .catch((err) => {
        console.error("PolicyHub fetch failed:", err);
        setError("Failed to fetch policies.");
      });
  }, [zip]);

  useEffect(() => {
    if (!search) {
      setFiltered(policies);
    } else {
      const term = search.toLowerCase();
      setFiltered(
        policies.filter(
          (p) =>
            p.title.toLowerCase().includes(term) ||
            p.summary.toLowerCase().includes(term)
        )
      );
    }
  }, [search, policies]);

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">Policy Browser</h2>
      <div className="flex gap-3 mb-6">
        <input
          type="text"
          placeholder="Search policies..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border rounded px-3 py-2 w-full"
        />
      </div>

      {error && <p className="text-red-500">{error}</p>}
      {filtered.length === 0 && <p className="text-gray-500">No results found.</p>}

      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
        {filtered.map((policy, i) => (
          <div key={i} className="border rounded p-4 shadow hover:shadow-md transition">
            <h3 className="font-semibold mb-2">{policy.title}</h3>
            <p className="text-sm text-gray-600 line-clamp-5">{policy.summary}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default PoliciesPage;
