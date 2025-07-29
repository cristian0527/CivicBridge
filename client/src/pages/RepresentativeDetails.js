import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const RepresentativeDetail = () => {
  const { bioguide_id } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/api/representative/${bioguide_id}`);
        if (!res.ok) throw new Error("Failed to fetch details");
        const json = await res.json();
        setData(json);
      } catch (err) {
        console.error(err);
        setError("Error loading representative details");
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [bioguide_id]);

  if (loading) return <p className="p-6">Loading...</p>;
  if (error) return <p className="p-6 text-red-500">{error}</p>;

  const { representative, legislative_activity, summary } = data;

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-2">{representative.name}</h2>
      <p className="text-gray-600 mb-4">
        {representative.party} • {representative.state} • {representative.chamber}
      </p>

      <div className="mb-6 space-y-1 text-sm text-gray-700">
        {representative.office_url && (
          <p>
            Website:{" "}
            <a
              href={representative.office_url}
              target="_blank"
              rel="noreferrer"
              className="text-blue-600 underline"
            >
              {representative.office_url}
            </a>
          </p>
        )}
      </div>

      <div className="mt-6">
        <h3 className="text-xl font-semibold mb-2">Legislative Activity</h3>
        <p className="text-sm text-gray-500 mb-2">
          Sponsored: {summary.sponsored_count} • Cosponsored: {summary.cosponsored_count}
        </p>
        <ul className="space-y-2">
          {legislative_activity.map((item, idx) => (
            <li key={idx} className="border p-3 rounded-md shadow-sm bg-white">
              <p className="font-medium">{item.title}</p>
              <p className="text-sm text-gray-600">{item.date}</p>
              <p className="text-sm text-gray-500">{item.position}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default RepresentativeDetail;
