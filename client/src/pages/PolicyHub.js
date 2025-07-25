import React from "react";
import { useLocation } from "react-router-dom";
import InfoCard from "../components/InfoCard";

const PolicyHub = () => {
  const { state } = useLocation();
  const { zip, role } = state || {};

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Relevant Policies for {role} in {zip}</h2>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <InfoCard title="Healthcare Reform" description="Affects Medicaid eligibility in your area." />
        <InfoCard title="Education Funding" description="Increased grants for students in your ZIP." />
        <InfoCard title="Transportation Bill" description="Expands public transit access in your city." />
      </div>
    </div>
  );
};

export default PolicyHub;