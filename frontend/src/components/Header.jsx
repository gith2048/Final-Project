import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

const Header = ({ isAuthenticated }) => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("currentUser");
    navigate("/");
  };

  return (
    <header className="bg-white text-blue-700 shadow-sm">
      <div className="max-w-7xl mx-auto flex justify-between items-center p-4">
        <Link to="/" className="flex items-center space-x-2">
          <img
            src="/assets/logo.png"
            alt="Optimus-PdM Logo"
            className="h-10 w-auto object-contain transition-transform duration-300 transform hover:scale-110 hover:rotate-3"
          />
          <span className="text-2xl font-bold hover:text-yellow-500 transition-colors duration-300">
            Optimus-PdM
          </span>
        </Link>

        <nav className="hidden md:flex space-x-6 items-center">
          <Link to="/" className="hover:text-yellow-500 transition">Home</Link>
          <Link to="/products" className="hover:text-yellow-500 transition">Products</Link>
          <Link to="/about" className="hover:text-yellow-500 transition">About Us</Link>
          <Link to="/contact" className="hover:text-yellow-500 transition">Contact</Link>
          {isAuthenticated ? (
            <>
              <Link to="/profile" className="hover:text-yellow-500 transition">Profile</Link>

              
            </>
          ) : (
            <Link to="/login" className="hover:text-yellow-500 transition">Login</Link>
          )}
        </nav>

        <button
          className="md:hidden focus:outline-none"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle navigation menu"
        >
          <svg className="w-6 h-6 text-blue-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            {isOpen ? (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>
      </div>

      <div className={`md:hidden bg-white px-4 pb-4 space-y-2 transition-all duration-300 ${
        isOpen ? "max-h-screen opacity-100" : "max-h-0 opacity-0 overflow-hidden"
      }`}>
        <Link to="/" className="block py-2 hover:text-yellow-500 transition">Home</Link>
        <Link to="/products" className="block py-2 hover:text-yellow-500 transition">Products</Link>
        <Link to="/about" className="block py-2 hover:text-yellow-500 transition">About Us</Link>
        <Link to="/contact" className="block py-2 hover:text-yellow-500 transition">Contact</Link>
        {isAuthenticated ? (
          <>
           <Link to="/profile" className="hover:text-yellow-500 transition">Profile</Link>

            
          </>
        ) : (
          <Link to="/login" className="block py-2 hover:text-yellow-500 transition">Login</Link>
        )}
      </div>
    </header>
  );
};

export default Header;