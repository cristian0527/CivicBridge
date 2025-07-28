import React from "react";
import ZipCodeForm from "../components/ZipCodeForm";

const Home = () => {
  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-5xl font-extrabold text-blue-900 text-center mb-6">
          CivicBridge
        </h1>
        <p className="text-center text-lg text-gray-700 max-w-2xl mx-auto mb-10 leading-relaxed">
          Most Americans can't keep up with the hundreds of policies passed each year.{" "}
          <span className="text-red-600 font-semibold">CivicBridge</span> gives you
          personalized, simple explanations tailored to your role in society.
        </p>
        <div className="flex justify-center">
          <ZipCodeForm />
        </div>
      </div>
    </div>
  );
};

export default Home;
