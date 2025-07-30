import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PoliciesPage = () => {
  const { state } = useLocation();
  const topic = state?.topic || "";
  const [policies, setPolicies] = useState([]);
  const [search, setSearch] = useState("");
  const [filtered, setFiltered] = useState([]);
  const [error, setError] = useState("");
  const [visibleCount, setVisibleCount] = useState(12);

  // Fetch policies by topic
  useEffect(() => {
    if (!topic) return;

    fetch(`${BACKEND_URL}/api/policyhub`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
          setPolicies([]);
        } else {
          setPolicies(data.policies || []);
        }
      })
      .catch((err) => {
        console.error("PolicyHub fetch failed:", err);
        setError("Failed to fetch policies.");
      });
  }, [topic]);

  // Filter by search input
  useEffect(() => {
    setVisibleCount(12); // Reset on search change
    const term = search.toLowerCase();
    setFiltered(
      policies.filter(
        (p) =>
          p.title.toLowerCase().includes(term) ||
          p.summary.toLowerCase().includes(term)
      )
    );
  }, [search, policies]);

  if (!topic) {
    return (
      <div className="p-6 max-w-4xl mx-auto text-center text-gray-500">
        No topic selected. Please go back and choose a policy topic to explore.
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h2 className="text-2xl font-bold mb-2">Policy Browser</h2>
      <p className="text-gray-600 mb-4">
        Showing {Math.min(visibleCount, filtered.length)} of {filtered.length} policies
        on <span className="capitalize font-semibold">{topic.replace("_", " ")}</span>
      </p>

      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <input
          type="text"
          placeholder="Search policies..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="border border-gray-300 rounded px-3 py-2 w-full focus:ring-2 focus:ring-blue-600 focus:outline-none"
        />
      </div>

      {error && <p className="text-red-500 mb-4">{error}</p>}
      {!error && filtered.length === 0 && (
        <p className="text-gray-500 mb-4">No results found for this topic.</p>
      )}

      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
        {filtered.slice(0, visibleCount).map((policy, i) => (
          <div
            key={i}
            className="border rounded p-4 shadow hover:shadow-md transition"
          >
            <h3 className="font-semibold mb-2">{policy.title}</h3>
            <p className="text-sm text-gray-600 line-clamp-5">{policy.summary}</p>
            <p className="mt-2 text-xs text-gray-400 italic">
              Source: {policy.source}
            </p>
          </div>
        ))}
      </div>

      {visibleCount < filtered.length && (
        <div className="mt-6 text-center">
          <button
            onClick={() => {
              setVisibleCount((prev) => prev + 12);
              setTimeout(() => {
                window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
              }, 100);
            }}
            className="bg-blue-700 hover:bg-blue-900 text-white px-6 py-2 rounded shadow transition"
          >
            Load More
          </button>
        </div>
      )}
    </div>
  );
};

export default PoliciesPage;
