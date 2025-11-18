import React, { useEffect, useState, useRef } from "react";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";
import axios from "axios";
import ChatWidget from "../pages/ChatWidget";
import RecommendationPanel from "../pages/RecommendationPanel";
import Panel from "../pages/Panel";
import GaugeCard from "../pages/GaugeCard";
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

  const [speed, setSpeed] = useState(0);
  const chatbotRef = useRef(null);

  const companyName = "TechNova Industries";
  const locationName = "Bangalore, India";

  const machines = [
    { id: 1, name: "Machine_A" },
    { id: 2, name: "Machine_B" },
    { id: 3, name: "Machine_C" },
  ];

  // Load logged user
  useEffect(() => {
    const savedUser = JSON.parse(localStorage.getItem("currentUser"));
    if (savedUser) setCurrentUser(savedUser);
  }, []);

  // -------------------------------
  // FETCH MACHINE DATA
  // -------------------------------
  useEffect(() => {
    if (!selectedMachine) return;

    const fetchData = async () => {
      try {
        const res = await axios.get("http://localhost:5000/api/sensor-data");

        const machineData = res.data[selectedMachine];

        if (!machineData) {
          console.error("Selected machine not found:", selectedMachine);
          return;
        }

        const DPs =20; // 👈 SET MAX DATAPOINTS
        const limited = {
          timestamps: machineData.timestamps.slice(-DPs),
          temperature: machineData.temperature.slice(-DPs),
          vibration: machineData.vibration.slice(-DPs),
          speed: machineData.speed.slice(-DPs),
        };

        setDashboardData(limited);
        calculateAverages(limited);
      } catch (err) {
        console.error("Error fetching sensor data:", err);
      }
    };

    fetchData();
  }, [selectedMachine]);

  // -------------------------------
  // LIVE RANDOM SENSOR SIMULATION
  // -------------------------------
 useEffect(() => {
  if (!dashboardData || !selectedMachine) return;

  const interval = setInterval(() => {
    setDashboardData(prev => {
      if (!prev) return prev;

      const rand = (v, a) => v + (Math.random() * a - a / 2);
      const spike = (v, chance, amt) =>
        Math.random() < chance ? v + (Math.random() < 0.5 ? amt : -amt) : v;

      let newTemp = rand(prev.temperature.at(-1), 3);
      newTemp = spike(newTemp, 0.2, 8);

      let newVib = rand(prev.vibration.at(-1), 0.5);
      newVib = spike(newVib, 0.15, 2);

      let newSpeed = rand(prev.speed.at(-1), 40);
      newSpeed = spike(newSpeed, 0.2, 120);

      return {
        timestamps: [...prev.timestamps.slice(1), new Date().toLocaleTimeString()],
        temperature: [...prev.temperature.slice(1), Math.max(0, newTemp)],
        vibration: [...prev.vibration.slice(1), Math.max(0, newVib)],
        speed: [...prev.speed.slice(1), Math.max(0, newSpeed)],
      };
    });
  }, 5000);

  return () => clearInterval(interval);
}, [dashboardData, selectedMachine]);

useEffect(() => {
  if (!dashboardData) return;
  calculateAverages(dashboardData);
}, [dashboardData]);


  // -------------------------------
  // CALCULATE AVERAGES
  // -------------------------------
const calculateAverages = (data) => {
  if (!data) return;

  const avg = {};

  // Compute average for ONLY 3 parameters
  ["temperature", "vibration", "speed"].forEach((key) => {
    const arr = data[key] || [];

    if (arr.length === 0) {
      avg[key] = 0;
    } else {
      const sum = arr.reduce((a, b) => a + b, 0);
      avg[key] = parseFloat((sum / arr.length).toFixed(2));
    }
  });

  setAverages(avg);

  // Update summary after setting averages
  setHealthSummary(
    getMachineHealthSummary(
      avg.temperature,
      avg.vibration,
      avg.speed
    )
  );
};



  // -------------------------------
  // MACHINE HEALTH SUMMARY
  // -------------------------------
  const getMachineHealthSummary = (temp, vib, speed) => {
    const issues = [];
    if (temp > 85) issues.push(`Temperature is critical at ${temp.toFixed(1)}°C.`);
    else if (temp > 75) issues.push(`Temperature is high at ${temp.toFixed(1)}°C.`);

    if (speed > 1350) issues.push(`Speed is critical at ${speed.toFixed(0)} RPM.`);
    else if (speed > 1200) issues.push(`Speed is high at ${speed.toFixed(0)} RPM.`);

    if (vib > 7) issues.push(`Vibration is critical at ${vib.toFixed(1)} mm/s.`);
    else if (vib > 5) issues.push(`Vibration is high at ${vib.toFixed(1)} mm/s.`);

    if (issues.length === 0) {
      return "✅ Machine is running normally. All parameters are within their expected ranges. No immediate action is required.";
    }

    const summary = issues.join(" ");
    return `⚠️ Machine requires attention. ${summary} Please monitor closely and consider inspection.`;
  };

  // -------------------------------
  // RENDER CHARTS
  // -------------------------------
  const renderCharts = () => {
    // Common Options
    const commonOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "top" },
        // ✅ Add a refined tooltip configuration for clarity
        tooltip: {
          enabled: true,
          backgroundColor: "rgba(0, 0, 0, 0.8)",
          titleColor: "#fff",
          bodyColor: "#fff",
          titleFont: { size: 14, weight: "bold" },
          bodyFont: { size: 12 },
          padding: 12,
          cornerRadius: 8,
          displayColors: true, // Show color boxes
          boxPadding: 3,
        },
        datalabels: { display: false }, // Hide datalabels
      },
      interaction: { intersect: false, mode: "index" },
      scales: {
        x: {
          ticks: {
            autoSkip: true, // ✅ Automatically skip labels to prevent overlap
            maxRotation: 0, // ✅ Keep labels horizontal
            minRotation: 0,
          },
        },
        y: {
          grid: {
            color: "rgba(0, 0, 0, 0.05)", // Lighter grid lines
            drawBorder: false,
          },
          ticks: {
            autoSkip: true,
            maxTicksLimit: 6,
            padding: 10, // Add padding to y-axis labels
          },
        },
      },
    };

    // Common options for a professional and interactive look
    
    Object.values(charts).forEach((c) => c?.destroy?.());
    const newCharts = {};

    const createChart = (id, type, data, opt) => {
      const ctx = document.getElementById(id)?.getContext("2d");
      if (ctx) newCharts[id] = new Chart(ctx, { type, data, opt });
    };

    // ✨ Gradient helper
    const createGradient = (ctx, color1, color2) => {
      const gradient = ctx.createLinearGradient(0, 0, 0, 400);
      gradient.addColorStop(0, color1);
      gradient.addColorStop(1, color2);
      return gradient;
    };

    // Get contexts for gradients
    const lineCtx = document.getElementById("lineChart")?.getContext("2d");
    const tempGradient = lineCtx ? createGradient(lineCtx, "rgba(231, 111, 81, 0.5)", "rgba(231, 111, 81, 0)") : "rgba(231,111,81,0.2)";
    const vibGradient = lineCtx ? createGradient(lineCtx, "rgba(42, 157, 143, 0.5)", "rgba(42, 157, 143, 0)") : "rgba(42,157,143,0.2)";


    // LINE: Temp + Vibration
    createChart(
      "lineChart",
      "line",
      {
        labels: dashboardData.timestamps,
        datasets: [
          {
            label: "Temperature (°C)",
            data: dashboardData.temperature,
            borderColor: "#e76f51",
            backgroundColor: tempGradient, // ✨ Use gradient
            fill: true,
            tension: 0.4, // ✨ Smoother lines
            pointRadius: 0, // ⚪ Hide points by default
            pointHoverRadius: 6, // Show on hover
            borderWidth: 2.5, // Thicker line
      },
          {
            label: "Vibration (mm/s)",
            data: dashboardData.vibration,
            borderColor: "#2a9d8f",
            backgroundColor: vibGradient, // ✨ Use gradient
            fill: true, // ✨ Smoother lines
            tension: 0.4,
            pointRadius: 0, // ⚪ Hide points by default
            pointHoverRadius: 6, // Show on hover
            borderWidth: 2.5, // Thicker line
          },
        ],
      },
      commonOptions
    );

    // BAR: Speed
    createChart(
      "barChart",
      "bar",
      {
        labels: dashboardData.timestamps,
        datasets: [
          {
            label: "Speed (RPM)",
          data: dashboardData.speed.map(s => Math.round(s)), // Round values
            backgroundColor: dashboardData.speed.map((s) =>
              s > 1200 ? "#dc2626" : "#4B9CD3"
            ),
            maxBarThickness: 50, // 📊 Consistent bar width
            borderRadius: 8,
          },
        ],
      },
      {
        ...commonOptions,
        plugins: {
          ...commonOptions.plugins,
          // ✅ Add datalabels to the bar chart
          datalabels: {
            display: true,
            anchor: "end",
            align: "top",
            color: "#666",
            font: { weight: "bold" },
            formatter: (value) => Math.round(value), // Show rounded value on top
          },
        },
      }
    );
    // PIE: Load Estimate
    createChart(
      "pieChart",
      "doughnut",
      {
        labels: ["High Load", "Medium Load", "Low Load"],
        datasets: [
          {
            data: [dashboardData.speed.at(-1) % 40, 40, 20],
            backgroundColor: ["#10B981", "#F59E0B", "#EF4444"],
          },
        ],
      },
      {
        responsive: true,
        cutout: "60%",
        plugins: {
          legend: { position: "top" },
          // ✅ Configure datalabels for the pie chart
          datalabels: {
            display: true,
            formatter: (value, ctx) => {
              const total = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
              const percentage = (value / total) * 100;
              // ✅ Hide label if slice is too small
              if (percentage < 10) return "";

              return percentage.toFixed(0) + "%";
            },
            color: "#fff", // White text for better contrast
          },
        },
      }
    );

    setCharts(newCharts);
  };

  useEffect(() => {
    if (dashboardData) renderCharts();
  }, [dashboardData]);

  // -------------------------------
const onDragStart = (e, chartId) => {
  e.dataTransfer.setData("chartId", chartId);
};

const onDragOver = (e) => {
  e.preventDefault();
};



  // DRAG + DROP ANALYSIS
  // -------------------------------
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
      }
    };

    const res = await axios.post("http://localhost:5000/chat/analyze", payload);

    // ⭐ SAVE ENTIRE RESPONSE
    setRecommendation(res.data);

    // ⭐ SAVE OVERALL SUMMARY FROM BACKEND for dashboard
    if (res.data.overall_summary) {
      setHealthSummary(res.data.overall_summary);
    }

    // ⭐ Chatbot speaks full recommendation from the new nested structure
    if (res.data?.overall_summary) {
      const { overall_summary, random_forest, isolation_forest } = res.data;

      // Construct a more detailed message for the chatbot
      const rf_msg = `Random Forest: ${random_forest.issue} - ${random_forest.solution}`;
      const iso_msg = `Isolation Forest: ${isolation_forest.issue} - ${isolation_forest.solution}`;

      const msg = `🧠 Analysis Complete:
${overall_summary}

${rf_msg}
${iso_msg}`;

      window.chatbot?.say?.(msg);
    }

  } catch (err) {
    console.error("Error analyzing chart:", err);
    alert("⚠️ Chatbot analysis failed. Check backend.");
  }
};


  // ------------------------------------
  // LABELS FOR COLAB
  // ------------------------------------
  const generateLabels = (avg) => {
    const set = (v, low, high, crit) =>
      v >= crit ? "critical" : v > high ? "high" : v >= low ? "medium" : "low";

    return {
      temperature: set(avg.temperature, 65, 75, 85),
      vibration: set(avg.vibration, 3, 5, 7),
      speed: set(avg.speed, 1150, 1250, 1350),
    };
  };

  // ------------------------------------
  // SEND TO COLAB / NGROK
  // ------------------------------------
  const handleSendToColab = async () => {
    try {
      const labels = generateLabels(averages);

      const res = await axios.post(
        "https://spaviet-shawnta-commonly.ngrok-free.dev/process",
        {
          temperature: dashboardData.temperature,
          vibration: dashboardData.vibration,
          speed: dashboardData.speed,
          email: currentUser?.email,
          machine_id: selectedMachine,
          labels,
        }
      );

      setReport(res.data);
      setAlerts(res.data.alerts || []);
      setShutdown(res.data.shutdown || false);
      setHealthSummary(res.data.health_summary || "");

      setEmailSent(true);
      setTimeout(() => setEmailSent(false), 8000);
    } catch (err) {
      console.error("Colab error", err);
      setEmailSent(false);
    }
  };
  

  // -------------------------------
  // UI START
  // -------------------------------
  return (
    <div
      className="min-h-screen bg-gray-100 p-6"
      onDrop={onDrop}
      onDragOver={(e) => e.preventDefault()}
    >
      {/* HEADER */}
      <div className="flex justify-between mb-6">
        <h1 className="text-3xl font-bold">Welcome {currentUser?.name}</h1>
        <button
          onClick={() => {
            localStorage.removeItem("currentUser");
            window.location.reload();
          }}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          Logout
        </button>
      </div>

      {/* MACHINE SELECTOR */}
      <div className="bg-white p-4 rounded shadow mb-6">
        <label className="font-semibold">Select Machine</label>
        <select
          className="border rounded p-2 ml-2"
          value={selectedMachine}
          onChange={(e) => setSelectedMachine(e.target.value)}
        >
          <option value="">--Select--</option>
          {machines.map((m) => (
            <option value={m.name} key={m.id}>
              {m.name}
            </option>
          ))}
        </select>
      </div>

      {/* PANELS */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <Panel title="First">
          <GaugeCard label="Temperature" value={averages.temperature} />
          <SliderControl label="Speed" value={speed} onChange={setSpeed} />
        </Panel>

        <Panel title="Second">
          <GaugeCard label="Vibration" value={averages.vibration} />
          <ColorPickerCard />
        </Panel>
      </div>

      {/* CHARTS */}
      {dashboardData && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div
  className="bg-white rounded-xl shadow-md p-4 cursor-grab hover:shadow-lg"
  draggable
  onDragStart={(e) => onDragStart(e, "lineChart")}
>
  <canvas id="lineChart" style={{ width: "100%", height: "220px" }}></canvas>
</div>

           <div
  className="bg-white rounded-xl shadow-md p-4 cursor-grab hover:shadow-lg"
  draggable
  onDragStart={(e) => onDragStart(e, "barChart")}
>
  <canvas id="barChart" style={{ width: "100%", height: "220px" }}></canvas>
</div>

          </div>

        <div
  className="bg-white rounded-xl shadow-md p-4 mb-6 cursor-grab hover:shadow-lg flex items-center justify-center"
  draggable
  onDragStart={(e) => onDragStart(e, "pieChart")}
  style={{ minHeight: "280px" }}
>
  <div style={{ width: "260px", height: "260px" }}>
    <canvas id="pieChart"></canvas>
  </div>
</div>




          {/* AVERAGES */}
          <div className="bg-white p-5 rounded shadow mb-6">
            <h3 className="font-semibold mb-4">Average Values</h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(averages).map(([key, val]) => {
                const level = generateLabels(averages)[key];
                const color =
                  level === "critical"
                    ? "bg-red-700 text-white"
                    : level === "high"
                    ? "bg-red-500 text-white"
                    : level === "medium"
                    ? "bg-yellow-400 text-black"
                    : "bg-green-500 text-white";

                return (
                  <div key={key} className="p-4 bg-blue-50 rounded shadow">
                    <h4 className="font-bold text-blue-700">{key.toUpperCase()}</h4>
                    <p className="text-xl mt-2">{val}</p>
                    <span className={`px-3 py-1 text-xs rounded-full mt-2 inline-block ${color}`}>
                      {level.toUpperCase()}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* ANALYZE BUTTON */}
          <div className="text-center mb-6">
            <button
              onClick={handleSendToColab}
              disabled={emailSent}
              className={`px-6 py-2 text-white rounded-lg ${
                emailSent ? "bg-gray-400" : "bg-green-600 hover:bg-green-700"
              }`}
            >
              {emailSent ? "Analyzing..." : "Analyze"}
            </button>
          </div>

          {/* REPORT */}
          {report && (
            <div className="bg-white p-5 rounded shadow mb-6">
              <h3 className="font-semibold mb-4">Machine Status Report</h3>
              <p><strong>Status:</strong> {report.status}</p>
              <p><strong>Avg Temp:</strong> {report.avg_temp}</p>
              <p><strong>Avg Vibration:</strong> {report.avg_vibration}</p>
              <p><strong>Avg Speed:</strong> {report.avg_speed}</p>

              {report.report_url && (
               <button
  className="px-4 py-2 bg-indigo-600 text-white rounded mt-4"
  onClick={() => {
    fetch(report.report_url, {
      method: "GET",
      headers: { "ngrok-skip-browser-warning": "true" }
    })
      .then((response) => {
        if (!response.ok) throw new Error("Failed downloading PDF");
        return response.blob();
      })
      .then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "Machine_Report.pdf";  // 👈 Forces download!
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      })
      .catch((err) => console.error("Download failed:", err));
  }}
>
  📄 Download PDF Report
</button>

              )}

            </div>
          )}

          {/* OVERALL SUMMARY */}
          {healthSummary && (
            <div className="bg-yellow-50 p-4 rounded-lg shadow mb-6">
              <h3 className="font-semibold text-lg text-yellow-800 mb-2">🧾 Overall Summary</h3>
              <p className="text-gray-800 whitespace-pre-line">{healthSummary}</p>
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
