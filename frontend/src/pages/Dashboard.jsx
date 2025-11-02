import React, { useEffect, useState, useRef } from "react";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";
import axios from "axios";
import ChatWidget from "../pages/ChatWidget";
import RecommendationPanel from "../pages/RecommendationPanel";


Chart.register(ChartDataLabels);

const Dashboard = () => {
  const [selectedMachine, setSelectedMachine] = useState("");
  const [dashboardData, setDashboardData] = useState(null);
  const [charts, setCharts] = useState({});
  const [averages, setAverages] = useState({});
  const [currentUser, setCurrentUser] = useState(null);
  const [droppedChart, setDroppedChart] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [report, setReport] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [shutdown, setShutdown] = useState(false);
  const [healthSummary, setHealthSummary] = useState("");

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
      vibration: [4.2, 4.5, 4.3, 4.6, 4.4, 4.7],
      speed: [1200, 1250, 1230, 1260, 1240, 1270],
    };
    setDashboardData(mockData);
    calculateAverages(mockData);
  }, [selectedMachine]);

const calculateAverages = (data) => {
  const avg = {};
  ["temperature", "vibration", "speed"].forEach((key) => {
    const values = data[key];
    const sum = values.reduce((a, b) => a + b, 0);
    avg[key] = parseFloat((sum / values.length).toFixed(2));
  });
  setAverages(avg);

  const summary = getMachineHealthSummary(avg.temperature, avg.vibration, avg.speed);
  setHealthSummary(summary);
};

  useEffect(() => {
    if (!dashboardData) return;

    const interval = setInterval(() => {
      const updated = { ...dashboardData };
      updated.temperature = updated.temperature.map((val) => val + (Math.random() * 2 - 1));
      updated.vibration = updated.vibration.map((val) => val + (Math.random() * 0.2 - 0.1));
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
    pointBackgroundColor: dashboardData.temperature.map((val) =>
      val > 75 ? "#dc2626" : "#e76f51"
    ),
  },
  {
    label: "Vibration (mm/s)",
    data: dashboardData.vibration,
    borderColor: "#2a9d8f",
    backgroundColor: "rgba(42, 157, 143, 0.15)",
    fill: true,
    tension: 0.4,
    pointBackgroundColor: dashboardData.vibration.map((val) =>
      val > 5.0 ? "#dc2626" : "#2a9d8f"
    ),
  },
],
    }, {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "bottom" },
        title: { display: true, text: "Temperature & Vibration Trends", color: "#264653" },
      },
    });

 createChart("barChart", "bar", {
  labels: dashboardData.timestamps,
  datasets: [
    {
      label: "Speed (RPM)",
      data: dashboardData.speed,
      backgroundColor: dashboardData.speed.map((val) =>
        val > 1200 ? "#dc2626" : "#4B9CD3"
      ),
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
    const payload = {
      temperature: dashboardData.temperature.at(-1),
      current: dashboardData.vibration.at(-1),
      speed: dashboardData.speed.at(-1),
      sequence: dashboardData.temperature.slice(-5)
    };

    const res = await axios.post("http://localhost:5000/predict", payload);
    setRecommendation(res.data); // ✅ This now contains all 3 model outputs

    // 🧠 Let the chatbot speak the summary
    if (res.data?.overall_summary) {
      window.chatbot?.say?.(res.data.overall_summary);
    }
  } catch (err) {
    console.error("Error fetching recommendation:", err);
    setRecommendation({
      error: true,
      message: "⚠️ Failed to analyze chart. Check backend logs."
    });
    window.chatbot?.say?.("⚠️ I couldn't analyze the chart. Please try again.");
  }
};
 const handleSendToColab = async () => {
  try {
    const payload = {
      temperature: dashboardData.temperature,
      vibration: dashboardData.vibration,
      speed: dashboardData.speed,
      email: currentUser?.email, // ✅ Send logged-in user's email
    };

    const res = await axios.post(
      "https://spaviet-shawnta-commonly.ngrok-free.dev/process",
      payload
    );

    setReport(res.data);
    setAlerts(res.data.alerts || []);
    setShutdown(res.data.shutdown);
    setHealthSummary(res.data.health_summary || "");
  } catch (err) {
    console.error("Error sending data to Colab:", err);
  }
};


const getMachineHealthSummary = (avgTemp, avgVibration, avgSpeed, threshold = 1200) => {
  if (avgTemp > 75 && avgSpeed > threshold) {
    return `⚠️ High temperature and speed detected. Inspect cooling systems and motor load to prevent wear.
Consistently elevated readings may indicate thermal stress and overdrive conditions.
This can reduce motor lifespan and increase energy consumption.
Immediate inspection is advised to prevent long-term damage.`;
  }

  if (avgTemp > 75) {
    return `⚠️ Temperature exceeds safe limits. Check for overheating, poor ventilation, or lubrication issues.
Sustained high temperatures can degrade components and affect performance.
Ensure cooling systems are functioning properly.
Schedule a thermal inspection to avoid downtime.`;
  }

  if (avgSpeed > threshold) {
    return `⚠️ Speed is above optimal range. Verify motor calibration and ensure load conditions are balanced.
Excessive RPM may cause wear, imbalance, or noise.
Monitor for signs of mechanical strain or instability.
Adjust operational parameters to maintain safe speed.`;
  }

  if (avgVibration > 5.0) {
    return `⚠️ Vibration levels are high. Inspect bearings, alignment, and structural integrity for faults.
Elevated vibration may signal imbalance, looseness, or wear in rotating parts.
If ignored, it can lead to mechanical failure or safety risks.
A preventive maintenance check is strongly recommended.`;
  }

  return `✅ The machine is operating within safe parameters. All metrics are stable and below critical thresholds.
No immediate action is required.
Continue monitoring for any future deviations.
System health is optimal at this time.`;
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

            {/* Alerts and Summary */}
      {alerts.length > 0 && (
        <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 my-4 rounded">
          <p className="font-bold">⚠️ Alerts:</p>
          <ul className="list-disc list-inside">
            {alerts.map((alert, idx) => (
              <li key={idx}>{alert}</li>
            ))}
          </ul>
          {shutdown && (
            <p className="mt-2 font-semibold text-yellow-800">
              ⚠️ Multiple sensors exceeded thresholds. Please turn off the system for a few hours and restart later.
            </p>
          )}
        </div>
      )}

      {healthSummary && (
        <div className="bg-gray-100 p-3 rounded shadow-sm mb-6">
          <p className="text-sm text-gray-800 font-medium">
            🩺 <strong>Health Summary:</strong> {healthSummary}
          </p>
        </div>
      )}

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
                  <p
                    className={`text-lg mt-2 ${
                      (key === "temperature" && value > 75) ||
                      (key === "vibration" && value > 5.0) ||
                      (key === "speed" && value > 1200)
                        ? "text-red-600 font-bold"
                        : "text-gray-800"
                    }`}
                  >
                    {value}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Analyze Button */}
          <div className="text-center mb-6">
            <button
              onClick={handleSendToColab}
              className="px-5 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 shadow"
            >
              Analyze
            </button>
          </div>

          {/* Report Section */}
          {report && (
            <div className="bg-white rounded-xl shadow-md p-5 mb-6">
              <h3 className="font-semibold text-gray-700 mb-4">Machine Status Report</h3>
              <p><strong>Status:</strong> {report.status}</p>
              <p><strong>Avg Temp:</strong> {report.avg_temp}</p>
              <p><strong>Avg Vibration:</strong> {report.avg_vibration}</p>
              <p><strong>Avg Speed:</strong> {report.avg_speed}</p>
              <a
                href={report.report_url}
                download="report.pdf"
                className="mt-3 inline-block px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
              >
                📄 Download PDF Report
              </a>
             {healthSummary && (
  <div style={{ marginTop: "1rem", padding: "12px", backgroundColor: "#f0f4ff", borderRadius: "8px" }}>
    <strong>📝 Overall Health Summary:</strong>
    <p style={{ whiteSpace: "pre-line" }}>{healthSummary}</p>
  </div>
)}
            </div>
          )}
        </>
      )}
       {recommendation && <RecommendationPanel data={recommendation} />}
      {/* Floating Chatbot Widget */}
      <ChatWidget chartData={dashboardData} />
    </div>
  );
};

export default Dashboard;