import React from "react";
import { Link } from "react-router-dom";

const Footer = () => {
  const year = new Date().getFullYear();
  return (
    <footer className="bg-gray-800 text-white pt-10">
      <div className="container mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 px-4">
        
        {/* About */}
        <div>
          <h3 className="text-xl font-bold mb-2">Optimus-PdM</h3>
          <p className="text-gray-300 mb-4">
            Leading the way in predictive maintenance solutions for industrial machinery. We help businesses reduce downtime and maintenance costs through innovative technology.
          </p>
          <div className="flex space-x-3">
            <a href="#" className="hover:text-blue-400"><i className="fab fa-facebook"></i></a>
            <a href="#" className="hover:text-blue-400"><i className="fab fa-twitter"></i></a>
            <a href="#" className="hover:text-blue-400"><i className="fab fa-linkedin"></i></a>
            <a href="#" className="hover:text-blue-400"><i className="fab fa-youtube"></i></a>
          </div>
        </div>

        {/* Quick Links */}
        <div>
          <h3 className="text-xl font-bold mb-2">Quick Links</h3>
          <ul className="space-y-1">
            <li><Link to="/" className="hover:text-blue-400">Home</Link></li>
            <li><Link to="/products" className="hover:text-blue-400">Products</Link></li>
           
            <li><Link to="/about" className="hover:text-blue-400">About Us</Link></li>
            <li><Link to="/contact" className="hover:text-blue-400">Contact</Link></li>
          </ul>
        </div>

        {/* Contact */}
        <div>
          <h3 className="text-xl font-bold mb-2">Contact Us</h3>
          <p className="flex items-start space-x-2 mb-2">
            <i className="fas fa-map-marker-alt mt-1"></i>
            <span>TOCE</span>
          </p>
          <p className="flex items-center space-x-2 mb-2">
            <i className="fas fa-phone"></i>
           
          </p>
          <p className="flex items-center space-x-2">
            <i className="fas fa-envelope"></i>
            <span>info@predictmaintain.com</span>
          </p>
        </div>
      </div>

      <div className="text-center text-gray-400 mt-8 pb-4">
        &copy; {year} Optimus-PdM. All Rights Reserved.
      </div>
    </footer>
  );
};

export default Footer;
