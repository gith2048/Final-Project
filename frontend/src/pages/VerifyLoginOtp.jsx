import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { toast, ToastContainer } from "react-toastify";

const VerifyLoginOtp = ({ setCurrentUser }) => {
  const [otp, setOtp] = useState("");
  const navigate = useNavigate();
  const location = useLocation();

  const email = location.state?.email || localStorage.getItem("pendingEmail");

  const handleVerify = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://localhost:5000/api/verify-login-otp", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, otp }),
      });

      const data = await response.json();

      if (!response.ok) {
        toast.error(data.message || "OTP verification failed");
        return;
      }

      // ✅ Save user and redirect
      localStorage.setItem("currentUser", JSON.stringify(data.user));
      localStorage.removeItem("pendingEmail");
      setCurrentUser(data.user);
      toast.success("Login successful!");
      setTimeout(() => navigate("/profile"), 1000);
    } catch (err) {
      console.error(err);
      toast.error("Something went wrong");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-4">
      <ToastContainer />
      <div className="bg-white p-6 rounded shadow w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Verify OTP</h2>
        <form onSubmit={handleVerify} className="space-y-4">
          <input
            type="text"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            placeholder="Enter OTP"
            className="w-full px-4 py-2 border rounded"
            required
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          >
            Verify and Continue
          </button>
        </form>
      </div>
    </div>
  );
};

export default VerifyLoginOtp;