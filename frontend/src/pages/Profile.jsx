import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FiEdit, FiUser, FiMail, FiLock, FiLogOut, FiMonitor, FiCheck, FiX } from "react-icons/fi";

const Profile = ({ currentUser, setCurrentUser }) => {
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
    setCurrentUser(null);
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
        setName(data.user.name);
        if (typeof currentUser === "object") {
          currentUser.name = data.user.name;
        }
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

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'active':
      case 'running':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'idle':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'maintenance':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header Section */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-6">
          <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-8 py-6">
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-lg">
                  <FiUser className="text-indigo-600 text-2xl" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-white">Profile Settings</h1>
                  <p className="text-indigo-100 text-sm mt-1">Manage your account information</p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-5 py-2.5 bg-white text-indigo-600 rounded-lg hover:bg-indigo-50 transition-all duration-200 font-medium shadow-md hover:shadow-lg"
              >
                <FiLogOut size={18} />
                Sign Out
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Account Information */}
          <div className="lg:col-span-2 space-y-6">
            {/* Personal Information Card */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                <FiUser className="text-indigo-600" />
                Personal Information
              </h2>
              
              <div className="space-y-5">
                {/* Name Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <FiUser size={16} className="text-gray-400" />
                    Full Name
                  </label>
                  {editMode ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        onBlur={handleSaveName}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            e.preventDefault();
                            handleSaveName();
                          }
                        }}
                        className="flex-1 border border-gray-300 px-4 py-2.5 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                        autoFocus
                      />
                      <button
                        onClick={handleSaveName}
                        className="p-2.5 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                        aria-label="Save"
                      >
                        <FiCheck size={18} />
                      </button>
                      <button
                        onClick={() => {
                          setEditMode(false);
                          setName(currentUser?.name || "");
                        }}
                        className="p-2.5 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                        aria-label="Cancel"
                      >
                        <FiX size={18} />
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between bg-gray-50 px-4 py-3 rounded-lg border border-gray-200">
                      <p className="text-gray-900 font-medium">{name}</p>
                      <button
                        onClick={() => setEditMode(true)}
                        className="text-indigo-600 hover:text-indigo-700 p-2 hover:bg-indigo-50 rounded-lg transition-all"
                        aria-label="Edit Name"
                      >
                        <FiEdit size={18} />
                      </button>
                    </div>
                  )}
                </div>

                {/* Email Field */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center gap-2">
                    <FiMail size={16} className="text-gray-400" />
                    Email Address
                  </label>
                  <div className="bg-gray-50 px-4 py-3 rounded-lg border border-gray-200">
                    <p className="text-gray-900 font-medium">{currentUser.email}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Security Card */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
                <FiLock className="text-indigo-600" />
                Security Settings
              </h2>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Reset Password
                </label>
                <div className="space-y-3">
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="Enter new password"
                    className="w-full border border-gray-300 px-4 py-2.5 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  />
                  <button
                    onClick={handleResetPassword}
                    disabled={!newPassword}
                    className="w-full sm:w-auto px-6 py-2.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-sm hover:shadow-md"
                  >
                    Update Password
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column - Quick Actions */}
          <div className="space-y-6">
            {/* Dashboard Access Card */}
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-white bg-opacity-20 rounded-lg flex items-center justify-center">
                  <FiMonitor className="text-2xl" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">Dashboard</h3>
                  <p className="text-indigo-100 text-sm">Monitor your machines</p>
                </div>
              </div>
              <button
                onClick={() => window.open("/dashboard", "_blank")}
                className="w-full px-4 py-3 bg-white text-indigo-600 rounded-lg hover:bg-indigo-50 transition-all duration-200 font-medium shadow-md hover:shadow-lg"
              >
                Open Dashboard
              </button>
            </div>

            {/* Stats Card */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Quick Stats</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center py-2 border-b border-gray-100">
                  <span className="text-gray-600 text-sm">Total Machines</span>
                  <span className="font-bold text-indigo-600 text-lg">
                    {summary ? summary.count : "..."}
                  </span>
                </div>
                <div className="flex justify-between items-center py-2">
                  <span className="text-gray-600 text-sm">Account Status</span>
                  <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                    Active
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Connected Machines Section */}
        <div className="mt-6 bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
              <FiMonitor className="text-indigo-600" />
              Connected Machines
            </h2>
            {summary && summary.count > 0 && (
              <span className="px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium">
                {summary.count} {summary.count === 1 ? 'Machine' : 'Machines'}
              </span>
            )}
          </div>
          
          {!summary ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-pulse flex flex-col items-center gap-3">
                <div className="w-12 h-12 bg-gray-200 rounded-full"></div>
                <p className="text-gray-500">Loading machine data...</p>
              </div>
            </div>
          ) : summary.count === 0 ? (
            <div className="text-center py-12">
              <FiMonitor className="mx-auto text-gray-300 text-5xl mb-4" />
              <p className="text-gray-500 text-lg">No machines connected yet</p>
              <p className="text-gray-400 text-sm mt-2">Connect your first machine to get started</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {summary.machines.map((machine) => (
                <div 
                  key={machine.id} 
                  className="border border-gray-200 rounded-lg p-5 hover:shadow-md transition-all duration-200 bg-gradient-to-br from-white to-gray-50"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                        <FiMonitor className="text-indigo-600" />
                      </div>
                      <div>
                        <h3 className="font-bold text-gray-900">{machine.name}</h3>
                        <p className="text-xs text-gray-500 mt-0.5">{machine.location}</p>
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(machine.status)}`}>
                      <span className="w-1.5 h-1.5 rounded-full bg-current mr-2"></span>
                      {machine.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;