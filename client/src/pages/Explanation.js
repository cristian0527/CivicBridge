import React from "react";
import { useLocation } from "react-router-dom";
import InfoCard from "../components/InfoCard";

const Explanation = () => {
  const { state } = useLocation();
  const { zip_code, role, explanation } = state || {};

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h2 className="text-2xl font-bold mb-4">
        Explanation for {role} in {zip_code}
      </h2>
      {explanation ? (
        <InfoCard title="Policy Summary" description={explanation} />
      ) : (
        <p>No explanation found.</p>
      )}
    </div>
  );
};

export default Explanation;