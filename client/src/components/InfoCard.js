import React from "react";

const InfoCard = ({ title, description }) => (
  <div className="border p-4 rounded shadow hover:shadow-md transition">
    <h3 className="font-bold text-lg mb-2">{title}</h3>
    <p className="text-sm text-gray-600">{description}</p>
  </div>
);

export default InfoCard;