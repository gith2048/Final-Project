import React, { useState, useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import AppLayout from "./pages/AppLayout";
import Home from "./pages/home";
import Products from "./pages/Products";
import Contact from "./pages/Contact";
import AboutUs from "./pages/AboutUs";
import Auth from "./pages/Auth";
import Dashboard from "./pages/Dashboard";
import ForgotPassword from "./pages/ForgotPassword";
import VerifyOtp from "./pages/VerifyOtp";
import ResetPassword from "./pages/ResetPassword";
import VerifyLoginOtp from "./pages/VerifyLoginOtp";
import Profile from "./pages/Profile";
import AOS from "aos";
import "aos/dist/aos.css";

function App() {
  const location = useLocation();
  const [currentUser, setCurrentUser] = useState(() => {
    const savedUser = localStorage.getItem("currentUser");
    return savedUser ? JSON.parse(savedUser) : null;
  });

  useEffect(() => {
    AOS.init({ duration: 1000 });
  }, []);

  const isDashboardView = location.pathname === "/dashboard";

  const routes = (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/products" element={<Products />} />
      <Route path="/contact" element={<Contact />} />
      <Route path="/about" element={<AboutUs />} />

      <Route
        path="/login"
        element={
          currentUser ? (
            <Navigate to="/profile" />
          ) : (
            <Auth setCurrentUser={setCurrentUser} />
          )
        }
      />
      <Route
        path="/signup"
        element={
          currentUser ? (
            <Navigate to="/profile" />
          ) : (
            <Auth setCurrentUser={setCurrentUser} />
          )
        }
      />

      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/verify-otp" element={<VerifyOtp />} />
      <Route
        path="/verify-login-otp"
        element={<VerifyLoginOtp setCurrentUser={setCurrentUser} />}
      />

      <Route
        path="/profile"
        element={
          currentUser ? (
            <Profile currentUser={currentUser} />
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/dashboard"
        element={
          currentUser ? (
            <Dashboard />
          ) : (
            <Navigate to="/login" />
          )
        }
      />

      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );

  return isDashboardView ? routes : (
    <AppLayout isAuthenticated={!!currentUser}>
      {routes}
    </AppLayout>
  );
}

export default App;