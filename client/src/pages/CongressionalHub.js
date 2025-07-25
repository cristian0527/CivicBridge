import React from "react";
import InfoCard from "../components/InfoCard";

const CongressionalHub = () => {
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">Your Elected Officials</h2>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <InfoCard title="Rep. Jane Doe (D)" description="U.S. House - Supports healthcare expansion." />
        <InfoCard title="Sen. John Smith (R)" description="U.S. Senate - Focuses on tax reform." />
        <InfoCard title="Gov. Sarah Lee (I)" description="State Governor - Education and jobs." />
      </div>
    </div>
  );
};

export default CongressionalHub;