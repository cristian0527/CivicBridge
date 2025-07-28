import React from "react";
import { Twitter } from "lucide-react";

const OfficialCard = ({ rep }) => {
  return (
    <div className="border rounded-xl shadow hover:shadow-md transition p-4 bg-white">
      <div className="flex items-center gap-4 mb-3">
        {rep.photo_url && (
          <img
            src={rep.photo_url}
            alt={rep.name}
            className="w-16 h-16 rounded-full object-cover border"
          />
        )}
        <div>
          <h3 className="text-lg font-semibold">
            {rep.name} ({rep.party || "N/A"})
          </h3>
          <p className="text-sm text-gray-500">{rep.title} - {rep.chamber}</p>
        </div>
      </div>
      <div className="text-sm space-y-1">
        {rep.district && <p><strong>District:</strong> {rep.district}</p>}
        <p><strong>State:</strong> {rep.state}</p>
        {rep.phone && <p><strong>Phone:</strong> {rep.phone}</p>}
        {rep.address && <p><strong>Address:</strong> {rep.address}</p>}
        {rep.website && (
          <p>
            <a href={rep.website} target="_blank" rel="noreferrer" className="text-blue-600 underline">
              Website
            </a>
          </p>
        )}
        {rep.contact_form && (
          <p>
            <a href={rep.contact_form} target="_blank" rel="noreferrer" className="text-blue-600 underline">
              Contact Form
            </a>
          </p>
        )}
        {rep.twitter && (
          <p className="flex items-center gap-1">
            <Twitter className="w-4 h-4 text-blue-500" />
            <a
              href={`https://twitter.com/${rep.twitter}`}
              target="_blank"
              rel="noreferrer"
              className="text-blue-600 underline"
            >
              @{rep.twitter}
            </a>
          </p>
        )}
      </div>
    </div>
  );
};

export default OfficialCard;
