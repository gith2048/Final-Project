import React, { useEffect, useState, useRef } from "react";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";
import axios from "axios";
import ChatWidget from "../pages/ChatWidget";

Chart.register(ChartDataLabels);

const Dashboard = () => {
  const [selectedMachine, setSelectedMachine] = useState("");
  const [dashboardData, setDashboardData] = useState(null);
  const [charts, setCharts] = useState({});
  const [averages, setAverages] = useState({});
  const [currentUser, setCurrentUser] = useState(null);
 
  const chatbotRef = useRef(null);

  const companyName = "TechNova Industries";
  const locationName = "Bangalore, India";
  const machines = [
    { id: 1, name: "Machine A" },
    { id: 2, name: "Machine B" },
    { id: 3, name: "Machine C" },
  ];

  useEffect(() => {
    const savedUser = JSON.parse(localStorage.getItem("currentUser"));
    if (savedUser) setCurrentUser(savedUser);
  }, []);

  useEffect(() => {
    if (!selectedMachine) return;
    const mockData = {
      timestamps: ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00"],
      temperature: [68, 70, 72, 71, 69, 73],
      current: [5.2, 5.5, 5.3, 5.6, 5.4, 5.7],
      speed: [1200, 1250, 1230, 1260, 1240, 1270],
    };
    setDashboardData(mockData);
    calculateAverages(mockData);
  }, [selectedMachine]);

  const calculateAverages = (data) => {
    const avg = {};
    ["temperature", "current", "speed"].forEach((key) => {
      const values = data[key];
      const sum = values.reduce((a, b) => a + b, 0);
      avg[key] = (sum / values.length).toFixed(2);
    });
    setAverages(avg);
  };

  useEffect(() => {
    if (!dashboardData) return;

    const interval = setInterval(() => {
      const updated = { ...dashboardData };
      updated.temperature = updated.temperature.map((val) => val + (Math.random() * 2 - 1));
      updated.current = updated.current.map((val) => val + (Math.random() * 0.2 - 0.1));
      updated.speed = updated.speed.map((val) => val + Math.floor(Math.random() * 20 - 10));
      setDashboardData(updated);
      calculateAverages(updated);
    }, 5000);

    return () => clearInterval(interval);
  }, [dashboardData]);

  const renderCharts = () => {
    Object.values(charts || {}).forEach((chart) => {
      if (chart && typeof chart.destroy === "function") chart.destroy();
    });

    const newCharts = {};

    const createChart = (id, type, data, options) => {
      const ctx = document.getElementById(id)?.getContext("2d");
      if (ctx) newCharts[id] = new Chart(ctx, { type, data, options });
    };

    createChart("lineChart", "line", {
      labels: dashboardData.timestamps,
      datasets: [
        {
          label: "Temperature (°C)",
          data: dashboardData.temperature,
          borderColor: "#e76f51",
          backgroundColor: "rgba(231, 111, 81, 0.15)",
          fill: true,
          tension: 0.4,
        },
        {
          label: "Current (A)",
          data: dashboardData.current,
          borderColor: "#2a9d8f",
          backgroundColor: "rgba(42, 157, 143, 0.15)",
          fill: true,
          tension: 0.4,
        },
      ],
    }, {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" },
        title: { display: true, text: "Temperature & Current Trends", color: "#264653" },
      },
    });

    createChart("barChart", "bar", {
      labels: dashboardData.timestamps,
      datasets: [
        {
          label: "Speed (RPM)",
          data: dashboardData.speed,
          backgroundColor: "#4B9CD3",
          borderRadius: 8,
          barThickness: 30,
        },
      ],
    }, {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        title: { display: true, text: "Speed Over Time", color: "#264653" },
        datalabels: {
          color: "#333",
          anchor: "end",
          align: "top",
          formatter: (v) => `${v} RPM`,
        },
      },
    });

    createChart("pieChart", "doughnut", {
      labels: ["High Load", "Medium Load", "Low Load"],
      datasets: [
        {
          label: "Machine Load",
          data: [
            dashboardData.speed[dashboardData.speed.length - 1] % 40,
            40,
            20,
          ],
          backgroundColor: ["#10B981", "#F59E0B", "#EF4444"],
          hoverOffset: 6,
        },
      ],
    }, {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "60%",
      plugins: {
        legend: { position: "bottom" },
        title: { display: true, text: "Machine Load Distribution", color: "#264653" },
      },
    });

    setCharts(newCharts);
  };

  useEffect(() => {
    if (!dashboardData) return;
    renderCharts();
  }, [dashboardData]);

  const handleLogout = () => {
    localStorage.removeItem("currentUser");
    window.location.reload();
  };

  const onDragStart = (e, chartId) => e.dataTransfer.setData("chartId", chartId);

  const onDrop = async (e) => {
    e.preventDefault();
    const chartId = e.dataTransfer.getData("chartId");
    if (!chartId || !dashboardData) return;

    setDroppedChart(chartId);
    setRecommendation(null);

    try {
      const res = await axios.post("http://localhost:5000/chat/analyze", {
        chartType: chartId,
        machineId: selectedMachine,
        data: dashboardData,
      });

      setRecommendation({
        issue: res.data.issue || "⚠️ No issue reported.",
        cause: res.data.cause || "Cause not identified.",
        solution: res.data.solution || "No solution available."
      });
    } catch (err) {
      console.error("Error fetching recommendation:", err);
      setRecommendation({
        issue: "⚠️ Failed to analyze chart.",
        cause: "Backend error or invalid data.",
        solution: "Check server logs and data format."
      });
    }
  };

  const onDragOver = (e) => e.preventDefault();

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800">
            Welcome, {currentUser?.name || "User"} 👋
          </h1>
          <p className="text-gray-600 mt-1">
            Monitoring Dashboard for {companyName} | {locationName}
          </p>
        </div>
        <button
          onClick={handleLogout}
          className="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 shadow"
        >
          Logout
        </button>
      </div>

      {/* Machine Selector */}
      <div className="bg-white rounded-xl shadow-md p-5 mb-6">
        <label className="font-semibold text-gray-700 block mb-2">Select Machine</label>
        <select
          value={selectedMachine}
          onChange={(e) => setSelectedMachine(e.target.value)}
          className="border p-2 rounded w-full md:w-1/3 focus:ring-2 focus:ring-blue-500"
        >
          <option value="">-- Select --</option>
          {machines.map((m) => (
            <option key={m.id} value={m.name}>{m.name}</option>
          ))}
        </select>
      </div>

      {/* Charts */}
     

      {/* Charts */}
      {dashboardData && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div
              className="bg-white rounded-xl shadow-md p-4 cursor-grab hover:shadow-lg"
              draggable
              onDragStart={(e) => onDragStart(e, "lineChart")}
            >
              <canvas id="lineChart" style={{ width: "100%", height: "350px" }}></canvas>
            </div>
            <div
              className="bg-white rounded-xl shadow-md p-4 cursor-grab hover:shadow-lg"
              draggable
              onDragStart={(e) => onDragStart(e, "barChart")}
            >
              <canvas id="barChart" style={{ width: "100%", height: "350px" }}></canvas>
            </div>
          </div>

          <div
            className="bg-white rounded-xl shadow-md p-4 mb-6 cursor-grab hover:shadow-lg"
            draggable
            onDragStart={(e) => onDragStart(e, "pieChart")}
          >
            <canvas id="pieChart" style={{ width: "100%", height: "250px" }}></canvas>
          </div>

          {/* Averages */}
          <div className="bg-white rounded-xl shadow-md p-5 mb-6">
            <h3 className="font-semibold text-gray-700 mb-4">Average Values</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(averages).map(([key, value]) => (
                <div
                  key={key}
                  className="bg-blue-50 text-center rounded-lg p-4 shadow hover:shadow-lg transition"
                >
                  <h4 className="text-blue-700 font-bold">{key.toUpperCase()}</h4>
                  <p className="text-gray-800 text-lg mt-2">{value}</p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

    

     

      {/* Floating Chatbot Widget */}
    <ChatWidget chartData={dashboardData} />
    </div>
  );
};

export default Dashboard;