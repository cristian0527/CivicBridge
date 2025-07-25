import React from "react";
import { Link } from "react-router-dom";

const Navbar = () => (
  <nav className="bg-blue-900 text-white px-6 py-4 flex items-center justify-between shadow">
  <Link to="/" className="text-2xl font-bold tracking-wide text-white">
    CivicBridge
  </Link>
  <div className="space-x-6 text-sm font-semibold">
    <Link to="/policies" className="hover:text-red-400 transition">Policies</Link>
    <Link to="/representatives" className="hover:text-red-400 transition">Representatives</Link>
  </div>
</nav>
);

export default Navbar;