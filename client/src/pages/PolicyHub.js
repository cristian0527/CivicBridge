import React from "react";
import { useLocation } from "react-router-dom";
import InfoCard from "../components/InfoCard";

const PolicyHub = () => {
  const { state } = useLocation();
  const { zip, role, policies } = state || {};

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">
        Relevant Policies for {role} in {zip}
      </h2>

      {policies?.length ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {policies.map((policy, index) => (
            <InfoCard
              key={index}
              title={policy.title}
              description={policy.summary}
            />
          ))}
        </div>
      ) : (
        <p>No policy data found. Try again.</p>
      )}
    </div>
  );
};

export default PolicyHub;
