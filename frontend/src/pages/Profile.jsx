import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Profile = ({ currentUser }) => {
  const [summary, setSummary] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [name, setName] = useState(currentUser?.name || "");
  const [newPassword, setNewPassword] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:5000/api/machine-summary")
      .then((res) => res.json())
      .then(setSummary)
      .catch((err) => console.error("Failed to fetch machine data:", err));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("currentUser");
    navigate("/login");
  };

  const handleSaveName = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/update-profile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: currentUser.email, name }),
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem("currentUser", JSON.stringify(data.user));
        setEditMode(false);
      } else {
        alert(data.message || "Update failed");
      }
    } catch (err) {
      console.error(err);
      alert("Something went wrong");
    }
  };

  const handleResetPassword = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: currentUser.email, password: newPassword }),
      });
      const data = await response.json();
      if (response.ok) {
        alert("Password reset successful");
        setNewPassword("");
      } else {
        alert(data.message || "Reset failed");
      }
    } catch (err) {
      console.error(err);
      alert("Something went wrong");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      <div className="max-w-4xl mx-auto bg-white shadow-md rounded-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Profile</h1>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
          >
            Sign Out
          </button>
        </div>

        {/* Name Edit */}
        <div className="mb-6">
          <label className="block font-semibold mb-1">Name</label>
          {editMode ? (
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="border px-3 py-2 rounded w-full"
            />
          ) : (
            <p className="text-gray-700">{name}</p>
          )}
        </div>

        <div className="mb-6">
          <label className="block font-semibold mb-1">Email</label>
          <p className="text-gray-700">{currentUser.email}</p>
        </div>

        <div className="flex gap-4 mb-6">
          {editMode ? (
            <>
              <button
                onClick={handleSaveName}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Save Name
              </button>
              <button
                onClick={() => setEditMode(false)}
                className="px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400"
              >
                Cancel
              </button>
            </>
          ) : (
            <button
              onClick={() => setEditMode(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Edit Name
            </button>
          )}
        </div>

        {/* Reset Password */}
        <div className="mb-6">
          <label className="block font-semibold mb-1">Reset Password</label>
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder="Enter new password"
            className="border px-3 py-2 rounded w-full mb-2"
          />
          <button
            onClick={handleResetPassword}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700"
          >
            Reset Password
          </button>
        </div>

        {/* Dashboard Button */}
<a
  href="/dashboard"
  target="_blank"
  rel="noopener noreferrer"
  className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
>
  Go to Dashboard
</a>

        {/* Machine Summary */}
        <h2 className="text-xl font-semibold mt-8 mb-4">Connected Machines</h2>
        {!summary ? (
          <p>Loading machine data...</p>
        ) : summary.count === 0 ? (
          <p>No machines connected.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {summary.machines.map((machine) => (
              <div key={machine.id} className="border p-4 rounded shadow-sm bg-gray-50">
                <h3 className="font-bold text-lg">{machine.name}</h3>
                <p className="text-sm text-gray-600">Location: {machine.location}</p>
                <p className="text-sm text-gray-600">Status: {machine.status}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Profile;