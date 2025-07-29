import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const UserProfileForm = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    zip_code: "",
    role: "",
    age: "",
    income_bracket: "",
    housing_status: "",
    healthcare_access: "",
    policy_choice: "1",
    custom_policy_text: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const payload = { ...formData };

      if (formData.policy_choice === "1") {
        payload.policy_text = formData.custom_policy_text;
      }

      const res = await fetch("http://localhost:5050/api/explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error("Server error");

      const data = await res.json();
      navigate("/explanation", { state: data });
    } catch (err) {
      console.error("Error:", err);
      setError("Failed to generate explanation. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 bg-white p-6 rounded-xl shadow max-w-md w-full"
    >
      <input
        name="zip_code"
        placeholder="ZIP code"
        required
        onChange={handleChange}
        className="w-full px-4 py-2 border rounded"
      />
      <input
        name="role"
        placeholder="Your role (e.g., engineer)"
        required
        onChange={handleChange}
        className="w-full px-4 py-2 border rounded"
      />
      <input
        name="age"
        placeholder="Age"
        type="number"
        required
        onChange={handleChange}
        className="w-full px-4 py-2 border rounded"
      />
      <input
        name="income_bracket"
        placeholder="Income bracket (low/middle/high)"
        required
        onChange={handleChange}
        className="w-full px-4 py-2 border rounded"
      />
      <input
        name="housing_status"
        placeholder="Housing status (renter/homeowner)"
        required
        onChange={handleChange}
        className="w-full px-4 py-2 border rounded"
      />
      <input
        name="healthcare_access"
        placeholder="Healthcare access (insured/uninsured/etc)"
        required
        onChange={handleChange}
        className="w-full px-4 py-2 border rounded"
      />

      <select
        name="policy_choice"
        onChange={handleChange}
        className="w-full px-4 py-2 border rounded"
        value={formData.policy_choice}
      >
        <option value="1">1. Enter a specific policy title or summary</option>
        <option value="2">2. Browse policies by topic</option>
        <option value="3">3. Get recent government rules</option>
        <option value="4">4. Search for policies</option>
        <option value="5">5. Browse current bills in Congress</option>
        <option value="6">6. Search Congressional bills</option>
        <option value="7">7. Get trending bills</option>
      </select>

      {formData.policy_choice === "1" && (
        <textarea
          name="custom_policy_text"
          placeholder="Paste a policy title, summary, or paragraph here"
          rows={4}
          className="w-full px-4 py-2 border rounded"
          onChange={handleChange}
          required
        />
      )}

      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-red-600 hover:bg-red-700 text-white font-bold rounded"
      >
        {loading ? "Generating..." : "Generate My Summary"}
      </button>

      {error && <p className="text-red-500 text-sm">{error}</p>}
    </form>
  );
};

export default UserProfileForm;
