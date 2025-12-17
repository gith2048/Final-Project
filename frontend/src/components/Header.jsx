import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";

const Header = ({ isAuthenticated }) => {
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const isDashboardPage = location.pathname === "/dashboard";

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

  const handleReturnToProfile = () => {
    // Close the current dashboard tab
    window.close();
    
    // Fallback: if window.close() doesn't work (some browsers restrict it),
    // navigate to profile page in the same tab
    setTimeout(() => {
      if (!window.closed) {
        navigate("/profile");
      }
    }, 100);
  };

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto flex justify-between items-center p-4">
        <Link to="/" className="flex items-center space-x-3 group relative">
         
          
          {/* Brand Text with Enhanced Styling */}
          <div className="flex flex-col relative">
            {/* Main Brand Name */}
            <div className="flex items-center space-x-2">
             <span className="text-3xl font-extrabold text-black tracking-tight relative">
  OPTIMUS
  {/* subtle depth for white background */}
  <span className="absolute inset-0 text-3xl font-extrabold text-black/15 blur-[1px]">
    OPTIMUS
  </span>
</span>

              
              {/* AI Chip Indicator */}
              <div className="flex items-center space-x-1">
                <div className="w-6 h-4 bg-gradient-to-r from-emerald-400 to-cyan-500 rounded-sm flex items-center justify-center shadow-lg">
                  <span className="text-[8px] font-bold text-white">AI</span>
                </div>
                <div className="w-1.5 h-1.5 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full animate-pulse"></div>
              </div>
            </div>
            
            {/* Subtitle with Tech Styling */}
            <div className="flex items-center space-x-1 -mt-1">
              <span className="text-xs font-bold text-gray-500 tracking-[0.15em] uppercase">
                Predictive
              </span>
              <div className="w-3 h-px bg-gradient-to-r from-gray-400 to-transparent"></div>
              <span className="text-xs font-bold text-gray-500 tracking-[0.15em] uppercase">
                Maintenance
              </span>
              <div className="w-3 h-px bg-gradient-to-r from-gray-400 to-transparent"></div>
              <span className="text-xs font-bold bg-gradient-to-r from-cyan-500 to-blue-600 bg-clip-text text-transparent tracking-[0.15em] uppercase">
                SYSTEM
              </span>
            </div>
            
            {/* Version Badge */}
            {/* <div className="absolute -top-1 -right-8 hidden xl:block">
              <span className="text-[8px] font-mono text-gray-400 bg-gray-100 px-1.5 py-0.5 rounded-full border">
                v2.1
              </span>
            </div> */}
          </div>
          
          {/* Advanced Status Panel */}
          <div className="hidden lg:flex items-center space-x-3 ml-4 pl-3 border-l border-gray-200">
            {/* System Status */}
            {/* <div className="flex flex-col items-center space-y-1">
              <div className="flex items-center space-x-1">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-lg shadow-green-400/50"></div>
                <div className="w-1 h-1 bg-green-300 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                <div className="w-0.5 h-0.5 bg-green-200 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
              </div>
              <span className="text-[9px] text-gray-400 font-mono tracking-wider">ONLINE</span>
            </div> */}
            
            {/* Data Stream Indicator */}
            {/* <div className="flex flex-col items-center space-y-1">
              <div className="flex space-x-0.5">
                {[...Array(3)].map((_, i) => (
                  <div 
                    key={i}
                    className="w-0.5 h-3 bg-gradient-to-t from-cyan-400 to-blue-500 rounded-full animate-pulse"
                    style={{animationDelay: `${i * 0.2}s`}}
                  ></div>
                ))}
              </div>
              <span className="text-[9px] text-gray-400 font-mono tracking-wider">SYNC</span>
            </div> */}
          </div>
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
                <button 
                  onClick={handleReturnToProfile}
                  className="font-semibold text-blue-600 hover:text-blue-700 transition"
                >
                  Return to Profile
                </button>
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
             <button 
               onClick={handleReturnToProfile}
               className="block py-2 text-blue-600 font-semibold hover:text-blue-700 transition text-left w-full"
             >
               Return to Profile
             </button>
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