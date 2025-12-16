import React, { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";

const Header = ({ isAuthenticated }) => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const isDashboardPage = location.pathname === "/dashboard";
  const isProfilePage = location.pathname === "/profile";

  const handleLogout = () => {
    // Clear user data
    localStorage.removeItem("currentUser");
    
    // If logging out from dashboard page, handle tab cleanup
    if (isDashboardPage) {
      // Signal other tabs to close/logout
      localStorage.setItem("logout-event", Date.now().toString());
      
      // Open login page in current tab and replace history
      window.location.replace("/login");
    } else {
      // Normal logout for other pages
      navigate("/login");
    }
  };

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto flex justify-between items-center p-4">
        <Link to="/" className="flex items-center space-x-2">
          
          <span className="text-4xl font-bold bg-gradient-to-tr from-sky-500 to-fuchsia-500 bg-clip-text text-transparent">
         Optimus-PdM
            </span>
        </Link>

        <nav className="hidden md:flex space-x-6 items-center">
          {!isDashboardPage && (
            <>
              <Link to="/" className="font-semibold">Home</Link>
              <Link to="/products" className="font-semibold">Products</Link>
              <Link to="/about" className="font-semibold">About Us</Link>
              <Link to="/contact" className="font-semibold">Contact</Link>
            </>
          )}
          {isAuthenticated ? (
            <>
              {isDashboardPage ? (
                <span className="font-semibold text-blue-600">Dashboard</span>
              ) : (
                <Link to="/profile" className="font-semibold">Profile</Link>
              )}
              {isDashboardPage && (
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition"
                >
                  Logout
                </button>
              )}
            </>
          ) : (
            <Link to="/login" className="font-semibold">Login</Link>
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
        {!isDashboardPage && (
          <>
            <Link to="/" className="block py-2 hover:text-yellow-500 transition">Home</Link>
            <Link to="/products" className="block py-2 hover:text-yellow-500 transition">Products</Link>
            <Link to="/about" className="block py-2 hover:text-yellow-500 transition">About Us</Link>
            <Link to="/contact" className="block py-2 hover:text-yellow-500 transition">Contact</Link>
          </>
        )}
        {isAuthenticated ? (
          <>
           {isDashboardPage ? (
             <span className="block py-2 text-blue-600 font-semibold">Dashboard</span>
           ) : (
             <Link to="/profile" className="hover:text-yellow-500 transition">Profile</Link>
           )}
           {isDashboardPage && (
             <button
               onClick={handleLogout}
               className="block py-2 text-red-600 hover:text-red-700 transition text-left"
             >
               Logout
             </button>
           )}
          </>
        ) : (
          <Link to="/login" className="block py-2 hover:text-yellow-500 transition">Login</Link>
        )}
      </div>
    </header>
  );
};

export default Header;