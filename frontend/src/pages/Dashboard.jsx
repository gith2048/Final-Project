import React, { useEffect, useState, useRef } from "react";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";
import axios from "axios";
import ChatWidget from "../pages/ChatWidget";
import RecommendationPanel from "../pages/RecommendationPanel";
import Panel from "../pages/Panel";
import GaugeCard from "../pages/GaugeCard";
import ChartCard from "../pages/ChartCard";
import SliderControl from "../pages/SliderControl";
import ColorPickerCard from "../pages/ColorPickerCard";

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
  const [emailSent, setEmailSent] = useState(false);
const [speed, setSpeed] = useState(averages.speed);
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

  // useEffect(() => {
  //   if (!selectedMachine) return;

  //   const mockData = {
  //     timestamps: ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00"],
  //     temperature: [68, 70, 72, 71, 69, 73],
  //     vibration: [4.2, 4.5, 4.3, 4.6, 4.4, 4.7],
  //     speed: [1200, 1250, 1230, 1260, 1240, 1270],
  //     current: [3.1, 3.2, 3.3, 3.2, 3.1, 3.4],
  //     noise: [65, 66, 67, 68, 66, 69],
  //   };

  //   setDashboardData(mockData);
  //   calculateAverages(mockData);
  // }, [selectedMachine]);



//  useEffect(() => {
//   if (!selectedMachine) return;

//   const fetchData = async () => {
//     try {
//       const res = await axios.get("http://localhost:5000/api/sensor-data");

//       // ⭐ LIMIT DATA HERE
//       const limited = limitData(res.data, 10); // show last 50 points

//       setDashboardData(limited);
//       calculateAverages(limited);

//     } catch (err) {
//       console.error("Error fetching sensor data:", err);
//     }
//   };

//   fetchData();
// }, [selectedMachine]);

// 🔹 FETCH DATA WHEN MACHINE IS SELECTED
useEffect(() => {
  if (!selectedMachine) return;  // ⛔ Don't fetch until user selects

  const fetchData = async () => {
    try {
      const res = await axios.get("http://localhost:5000/api/sensor-data");

      const limited = limitData(res.data, 10);

      setDashboardData(limited);
      calculateAverages(limited);

    } catch (err) {
      console.error("Error fetching sensor data:", err);
    }
  };

  fetchData();
}, [selectedMachine]);  // 🔥 Only runs after selecting machine



useEffect(() => {
  if (!dashboardData || !selectedMachine) return;

  const clamp = (value, min) => Math.max(value, min);  // ⛔ Prevent negatives

  const interval = setInterval(() => {
    setDashboardData(prev => {
      if (!prev) return prev;

      const rand = (base, amount) =>
        base + (Math.random() * amount - amount / 2);

      const spike = (value, chance, amount) =>
        Math.random() < chance ? value + amount * (Math.random() > 0.5 ? 1 : -1) : value;

      let newTemp = clamp(rand(prev.temperature.at(-1), 4), 0);
      newTemp = clamp(spike(newTemp, 0.2, 10), 0);

      let newVib = clamp(rand(prev.vibration.at(-1), 0.5), 0);
      newVib = clamp(spike(newVib, 0.15, 2), 0);

      let newSpeed = clamp(rand(prev.speed.at(-1), 40), 0);
      newSpeed = clamp(spike(newSpeed, 0.2, 120), 0);

      let newCurrent = clamp(rand(prev.current.at(-1), 0.3), 0);
      newCurrent = clamp(spike(newCurrent, 0.1, 1), 0);

      let newNoise = clamp(rand(prev.noise.at(-1), 5), 0);
      newNoise = clamp(spike(newNoise, 0.2, 15), 0);

      return {
        timestamps: [...prev.timestamps.slice(1), new Date().toLocaleTimeString()],
        temperature: [...prev.temperature.slice(1), newTemp],
        vibration: [...prev.vibration.slice(1), newVib],
        speed: [...prev.speed.slice(1), newSpeed],
        current: [...prev.current.slice(1), newCurrent],
        noise: [...prev.noise.slice(1), newNoise],
      };
    });
  }, 5000);

  return () => clearInterval(interval);
}, [dashboardData, selectedMachine]);


useEffect(() => {
  if (!dashboardData) return;
  calculateAverages(dashboardData);
}, [dashboardData]);







  const calculateAverages = (data) => {
    const avg = {};
    ["temperature", "vibration", "speed", "current", "noise"].forEach((key) => {
      const values = data[key];
      const sum = values.reduce((a, b) => a + b, 0);
      avg[key] = parseFloat((sum / values.length).toFixed(2));
    });
    setAverages(avg);

    const summary = getMachineHealthSummary(
      avg.temperature,
      avg.vibration,
      avg.speed,
      avg.noise
    );
    setHealthSummary(summary);
  };


  const limitData = (data, size = 10) => {
  return {
    timestamps: data.timestamps.slice(-size),
    temperature: data.temperature.slice(-size),
    vibration: data.vibration.slice(-size),
    speed: data.speed.slice(-size),
    current: data.current.slice(-size),
    noise: data.noise.slice(-size)
  };
};


  // useEffect(() => {
  //   if (!dashboardData) return;

  //   const interval = setInterval(() => {
  //     const updated = { ...dashboardData };
  //     updated.temperature = updated.temperature.map((val) => val + (Math.random() * 2 - 1));
  //     updated.vibration = updated.vibration.map((val) => val + (Math.random() * 0.2 - 0.1));
  //     updated.speed = updated.speed.map((val) => val + Math.floor(Math.random() * 20 - 10));
  //     updated.current = updated.current.map((val) => val + (Math.random() * 0.2 - 0.1));
  //     updated.noise = updated.noise.map((val) => val + Math.floor(Math.random() * 3 - 1));
  //     setDashboardData(updated);
  //     calculateAverages(updated);
  //   }, 5000);

  //   return () => clearInterval(interval);
  // }, [dashboardData]);

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
            dashboardData.speed.at(-1) % 40,
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
  const onDragOver = (e) => e.preventDefault();

  const onDrop = async (e) => {
  e.preventDefault();
  const chartId = e.dataTransfer.getData("chartId");
  if (!chartId || !dashboardData) return;

  setDroppedChart(chartId);
  setRecommendation(null);

  try {
    const payload = {
      chartType: chartId,
      data: {
        temperature: dashboardData.temperature,
        speed: dashboardData.speed,
        vibration: dashboardData.vibration,
        current: dashboardData.current,
        noise: dashboardData.noise
      }
    };

    const res = await axios.post("http://localhost:5000/chat/analyze", payload);
    setRecommendation(res.data);

    if (res.data?.issue) {
      const summary = `🧠 Recommendation:\n• Issue: ${res.data.issue}\n• Cause: ${res.data.cause}\n• Solution: ${res.data.solution}`;
      window.chatbot?.say?.(summary);
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

const generateLabels = (avg) => {
  const label = (val, low, high, critical) =>
    val >= critical ? "critical" :
    val > high ? "high" :
    val >= low ? "medium" :
    "low";

  return {
    // 🌡 TEMPERATURE (°C)
    temperature: label(avg.temperature, 65, 75, 85),

    // ⚙ SPEED (RPM)
    speed: label(avg.speed, 1150, 1250, 1350),  // fixed critical threshold

    // 📈 VIBRATION (mm/s)
    vibration: label(avg.vibration, 3.0, 5.0, 7.0),

    // 🔌 CURRENT (A) — fixed low threshold
    current: label(avg.current, 3.5, 4.5, 5.0),

    // 🔊 NOISE (dB) — fixed low threshold
    noise: label(avg.noise, 70, 80, 90),
  };
};


const handleSendToColab = async () => {
  try {
    const labels = generateLabels(averages);
    const hasCritical = Object.values(labels).includes("critical");

    // Prevent spam of repeated critical alerts
    if (hasCritical && emailSent) {
      console.warn("🚨 Critical alert already sent. Skipping duplicate email.");
      return;
    }

    const payload = {
      temperature: dashboardData.temperature,
      speed: dashboardData.speed,
      vibration: dashboardData.vibration,
      current: dashboardData.current,
      noise: dashboardData.noise,
      email: currentUser?.email,
      machine_id: selectedMachine,
      labels: labels,
    };

    const res = await axios.post(
      "https://spaviet-shawnta-commonly.ngrok-free.dev/process",
      payload
    );

    setReport(res.data);
    setAlerts(res.data.alerts || []);
    setShutdown(res.data.shutdown);
    setHealthSummary(res.data.health_summary || "");

    // Disable button temporarily (for UI feedback)
    setEmailSent(true);

    // 🔥 Re-enable analyze button after 10 seconds
    setTimeout(() => {
      setEmailSent(false);
    }, 10000);

    if (hasCritical) {
      console.log("🚨 Critical alert email triggered.");
    }

  } catch (err) {
    console.error("Error sending data to Colab:", err);

    // Re-enable analyze button if API fails
    setEmailSent(false);
  }
};


  const getMachineHealthSummary = (avgTemp, avgVibration, avgSpeed, avgNoise, threshold = 1200) => {
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

    if (avgNoise > 80) {
      return `⚠️ Noise levels are elevated. Check for loose components, worn insulation, or misalignment.
High noise may indicate mechanical stress or poor acoustic shielding.
Inspect housing and motor mounts for vibration transfer.`;
    }

    return `✅ The machine is operating within safe parameters. All metrics are stable and below critical thresholds.
No immediate action is required.
Continue monitoring for any future deviations.
System health is optimal at this time.`;
  };

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

    <div className="grid grid-cols-1 md:grid-cols-3 gap-x-6 gap-y-8 mb-6">
  <Panel title="First">
    {/* ✅ Paste here */}
    <GaugeCard label="Temperature" value={averages.temperature} />
    <SliderControl label="Speed" value={speed} onChange={(val) => setSpeed(val)} />
  </Panel>

  <Panel title="Second">
    <GaugeCard label="Vibration" value={averages.vibration} />
    <ColorPickerCard />
  </Panel>
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
            {Object.entries(averages).map(([key, value]) => {
              const level = generateLabels(averages)[key];
              const badgeColor = {
                critical: "bg-red-800 text-white",
                high: "bg-red-500 text-white",
                medium: "bg-yellow-400 text-black",
                low: "bg-green-500 text-white",
              }[level];

              return (
                <div key={key} className="bg-blue-50 text-center rounded-lg p-4 shadow hover:shadow-lg transition">
                  <h4 className="text-blue-700 font-bold">{key.toUpperCase()}</h4>
                  <p className={`text-lg mt-2 ${level === "critical" ? "text-red-800 font-extrabold" :
                                                level === "high" ? "text-red-600 font-bold" :
                                                level === "medium" ? "text-yellow-600 font-semibold" :
                                                "text-gray-800"}`}>
                    {value}
                  </p>
                  <span className={`mt-2 inline-block px-2 py-1 text-xs rounded-full ${badgeColor}`}>
                    {level.toUpperCase()}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Analyze Button */}
        <div className="text-center mb-6">
          <button
            onClick={handleSendToColab}
            disabled={emailSent}
            className={`px-5 py-2 rounded-lg shadow text-white ${
              emailSent ? "bg-gray-400 cursor-not-allowed" : "bg-green-600 hover:bg-green-700"
            }`}
          >
            {emailSent ? "Alert Sent" : "Analyze"}
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
            <p><strong>Avg Current:</strong> {report.avg_current}</p>
            <p><strong>Avg Noise:</strong> {report.avg_noise}</p>

            {/* Download Report */}
            {report.report_url && (
              <div className="mt-4">
                <button
                  onClick={() => {
                    fetch(report.report_url, {
                      headers: { "ngrok-skip-browser-warning": "true" }
                    })
                      .then(response => {
                        if (!response.ok) throw new Error("Network response was not ok");
                        return response.blob();
                      })
                      .then(blob => {
                        const url = window.URL.createObjectURL(blob);
                        const link = document.createElement("a");
                        link.href = url;
                        link.download = "Machine_Report.pdf";
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        window.URL.revokeObjectURL(url);
                      })
                      .catch(err => console.error("Download failed:", err));
                  }}
                  className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 inline-block"
                >
                  📄 Download PDF Report
                </button>
              </div>
            )}

            {/* Health Summary */}
            {healthSummary && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <strong>📝 Overall Health Summary:</strong>
                <p style={{ whiteSpace: "pre-line" }}>{healthSummary}</p>
              </div>
            )}
          </div>
        )}
      </>
    )}

    {recommendation && <RecommendationPanel data={recommendation} />}
    <ChatWidget chartData={dashboardData} />
  </div>
);
};

export default Dashboard;