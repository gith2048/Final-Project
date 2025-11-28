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

const SEQ_LEN = 10; // LSTM sequence length (must match backend)

const Dashboard = () => {
  const [selectedMachine, setSelectedMachine] = useState("");
  const [dashboardData, setDashboardData] = useState(null);
  const [charts, setCharts] = useState({});
  const [averages, setAverages] = useState({ temperature: 0, vibration: 0, speed: 0 });
  const [currentUser, setCurrentUser] = useState(null);
  const [droppedChart, setDroppedChart] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [report, setReport] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [shutdown, setShutdown] = useState(false);
  const [healthSummary, setHealthSummary] = useState("");
  const [emailSent, setEmailSent] = useState(false);

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
    try {
      const savedUser = JSON.parse(localStorage.getItem("currentUser"));
      if (savedUser) setCurrentUser(savedUser);
    } catch {
      setCurrentUser(null);
    }
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
          setDashboardData(null);
          return;
        }

        const DPs = 20; // max datapoints
        const limited = {
          timestamps: machineData.timestamps.slice(-DPs),
          temperature: machineData.temperature.slice(-DPs).map(Number),
          vibration: machineData.vibration.slice(-DPs).map(Number),
          speed: machineData.speed.slice(-DPs).map(Number),
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
  // LIVE RANDOM SENSOR SIMULATION (keeps UI active)
  // -------------------------------
  useEffect(() => {
    if (!dashboardData || !selectedMachine) return;

    const interval = setInterval(() => {
      setDashboardData((prev) => {
        if (!prev) return prev;

        const rand = (v, a) => Number(v) + (Math.random() * a - a / 2);
        const spike = (v, chance, amt) =>
          Math.random() < chance ? v + (Math.random() < 0.5 ? amt : -amt) : v;

        const lastTemp = Number(prev.temperature.at(-1) ?? 60);
        const lastVib = Number(prev.vibration.at(-1) ?? 2);
        const lastSpeed = Number(prev.speed.at(-1) ?? 1000);

        let newTemp = rand(lastTemp, 3);
        newTemp = spike(newTemp, 0.2, 8);

        let newVib = rand(lastVib, 0.5);
        newVib = spike(newVib, 0.15, 2);

        let newSpeed = rand(lastSpeed, 40);
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

  // update averages whenever dashboardData changes
  useEffect(() => {
    if (dashboardData) calculateAverages(dashboardData);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dashboardData]);

  // -------------------------------
  // CALCULATE AVERAGES
  // -------------------------------
  const calculateAverages = (data) => {
    if (!data) return;

    const avg = {};
    ["temperature", "vibration", "speed"].forEach((key) => {
      const arr = data[key] || [];
      if (arr.length === 0) {
        avg[key] = 0;
      } else {
        const sum = arr.reduce((a, b) => a + Number(b || 0), 0);
        avg[key] = parseFloat((sum / arr.length).toFixed(2));
      }
    });

    setAverages(avg);

    // Update summary after setting averages
    setHealthSummary(getMachineHealthSummary(avg.temperature, avg.vibration, avg.speed));
  };

  // -------------------------------
  // MACHINE HEALTH SUMMARY
  // -------------------------------
  const getMachineHealthSummary = (temp, vib, speedVal) => {
    const issues = [];
    if (temp > 85) issues.push(`Temperature is critical at ${temp.toFixed(1)}°C.`);
    else if (temp > 75) issues.push(`Temperature is high at ${temp.toFixed(1)}°C.`);

    if (speedVal > 1350) issues.push(`Speed is critical at ${speedVal.toFixed(0)} RPM.`);
    else if (speedVal > 1200) issues.push(`Speed is high at ${speedVal.toFixed(0)} RPM.`);

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
    if (!dashboardData) return;

    // Common Options
    const commonOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "top" },
        tooltip: {
          enabled: true,
          backgroundColor: "rgba(0, 0, 0, 0.8)",
          titleColor: "#fff",
          bodyColor: "#fff",
          padding: 12,
          cornerRadius: 8,
          displayColors: true,
          boxPadding: 3,
        },
        datalabels: { display: false },
      },
      interaction: { intersect: false, mode: "index" },
      scales: {
        x: {
          ticks: {
            autoSkip: true,
            maxRotation: 0,
            minRotation: 0,
          },
        },
        y: {
          grid: {
            color: "rgba(0, 0, 0, 0.05)",
            drawBorder: false,
          },
          ticks: {
            autoSkip: true,
            maxTicksLimit: 6,
            padding: 10,
          },
        },
      },
    };

    // Destroy old charts
    Object.values(charts).forEach((c) => c?.destroy?.());
    const newCharts = {};

    const createChart = (id, type, data, opt) => {
      const ctx = document.getElementById(id)?.getContext("2d");
      if (ctx) newCharts[id] = new Chart(ctx, { type, data, options: opt });
    };

    // Gradient helper
    const createGradient = (ctx, color1, color2) => {
      const gradient = ctx.createLinearGradient(0, 0, 0, 400);
      gradient.addColorStop(0, color1);
      gradient.addColorStop(1, color2);
      return gradient;
    };

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
            backgroundColor: tempGradient,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 6,
            borderWidth: 2.5,
          },
          {
            label: "Vibration (mm/s)",
            data: dashboardData.vibration,
            borderColor: "#2a9d8f",
            backgroundColor: vibGradient,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 6,
            borderWidth: 2.5,
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
            data: dashboardData.speed.map((s) => Math.round(s)),
            backgroundColor: dashboardData.speed.map((s) => (s > 1200 ? "#dc2626" : "#4B9CD3")),
            maxBarThickness: 50,
            borderRadius: 8,
          },
        ],
      },
      {
        ...commonOptions,
        plugins: {
          ...commonOptions.plugins,
          datalabels: {
            display: true,
            anchor: "end",
            align: "top",
            color: "#666",
            font: { weight: "bold" },
            formatter: (value) => Math.round(value),
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
          datalabels: {
            display: true,
            formatter: (value, ctx) => {
              const total = ctx.chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
              const percentage = (value / total) * 100;
              if (percentage < 10) return "";
              return percentage.toFixed(0) + "%";
            },
            color: "#fff",
          },
        },
      }
    );

    setCharts(newCharts);
  };

  useEffect(() => {
    if (dashboardData) renderCharts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

    // Get chart name for display
    const chartNames = {
      lineChart: "Temperature & Vibration Chart",
      barChart: "Speed Chart",
      pieChart: "Load Distribution Chart"
    };
    const chartName = chartNames[chartId] || chartId;

    // Notify chatbot: Chart dropped
    try {
      if (window.chatbot && typeof window.chatbot.say === "function") {
        window.chatbot.say(`📊 ${chartName} received! Analyzing machine condition...`);
      }
    } catch (err) {
      console.warn("chatbot notification failed", err);
    }

    try {
      const payload = {
        chartType: chartId,
        data: {
          temperature: dashboardData.temperature,
          speed: dashboardData.speed,
          vibration: dashboardData.vibration,
        },
        email: currentUser?.email,  // Add user email for alert system
        machine_id: selectedMachine,  // Add machine ID for alert system
      };

      // Attach sequence if available (SEQ_LEN x 3)
      if (
        Array.isArray(dashboardData.temperature) &&
        dashboardData.temperature.length >= SEQ_LEN &&
        dashboardData.vibration.length >= SEQ_LEN &&
        dashboardData.speed.length >= SEQ_LEN
      ) {
        payload.sequence = [];
        const t = dashboardData.temperature.slice(-SEQ_LEN);
        const v = dashboardData.vibration.slice(-SEQ_LEN);
        const s = dashboardData.speed.slice(-SEQ_LEN);
        for (let i = 0; i < SEQ_LEN; i++) payload.sequence.push([t[i], v[i], s[i]]);
      }

      const res = await axios.post("http://localhost:5000/chat/analyze", payload);

      // SAVE ENTIRE RESPONSE
      setRecommendation(res.data);

      // SAVE OVERALL SUMMARY FROM BACKEND for dashboard
      if (res.data.overall_summary) setHealthSummary(res.data.overall_summary);

      // Chatbot speaks full recommendation from the new nested structure
      if (res.data?.overall_summary) {
        const { overall_summary, random_forest, isolation_forest, lstm, recommendations } = res.data;

        // Build detailed recommendation message with better formatting
        let detailedMsg = `🧠 Analysis Complete for ${chartName}\n\n`;
        detailedMsg += `${overall_summary}\n\n`;

        // LSTM Forecast
        if (lstm?.forecast) {
          detailedMsg += `🔮 LSTM Forecast (Next Cycle):\n`;
          detailedMsg += `• Temperature: ${lstm.forecast.temperature.toFixed(1)}°C\n`;
          detailedMsg += `• Vibration: ${lstm.forecast.vibration.toFixed(2)} mm/s\n`;
          detailedMsg += `• Speed: ${lstm.forecast.speed.toFixed(0)} RPM\n\n`;
        }

        // Random Forest
        if (random_forest) {
          detailedMsg += `🌲 Random Forest Classification:\n`;
          detailedMsg += `• Status: ${random_forest.issue}\n`;
          if (random_forest.cause) {
            detailedMsg += `• Cause: ${random_forest.cause}\n`;
          }
          if (random_forest.solution) {
            detailedMsg += `• Recommendation: ${random_forest.solution}\n\n`;
          }
        }

        // Isolation Forest
        if (isolation_forest) {
          detailedMsg += `🔍 Anomaly Detection:\n`;
          detailedMsg += `• Status: ${isolation_forest.issue}\n`;
          if (isolation_forest.cause) {
            detailedMsg += `• Cause: ${isolation_forest.cause}\n`;
          }
          if (isolation_forest.solution) {
            detailedMsg += `• Action: ${isolation_forest.solution}\n\n`;
          }
        }

        // INTELLIGENT RECOMMENDATIONS (NEW!)
        if (recommendations) {
          detailedMsg += `\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
          detailedMsg += `💡 INTELLIGENT RECOMMENDATIONS & SOLUTIONS\n`;
          detailedMsg += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;
          detailedMsg += `${recommendations.summary}\n\n`;

          // Display actions based on priority
          if (recommendations.actions && recommendations.actions.length > 0) {
            recommendations.actions.forEach((action, idx) => {
              detailedMsg += `${action.icon} ${action.title}\n`;
              detailedMsg += `${'─'.repeat(50)}\n`;
              detailedMsg += `Problem: ${action.problem}\n`;
              detailedMsg += `Impact: ${action.impact}\n\n`;

              if (action.root_causes && action.root_causes.length > 0) {
                detailedMsg += `🔍 Possible Root Causes:\n`;
                action.root_causes.forEach(cause => {
                  detailedMsg += `  • ${cause}\n`;
                });
                detailedMsg += `\n`;
              }

              if (action.immediate_actions && action.immediate_actions.length > 0) {
                detailedMsg += `⚡ IMMEDIATE ACTIONS:\n`;
                action.immediate_actions.forEach(step => {
                  detailedMsg += `  ${step}\n`;
                });
                detailedMsg += `\n`;
              }

              if (action.resolution_steps && action.resolution_steps.length > 0) {
                detailedMsg += `🔧 RESOLUTION STEPS:\n`;
                action.resolution_steps.forEach(step => {
                  detailedMsg += `  ${step}\n`;
                });
                detailedMsg += `\n`;
              }

              if (action.prevention && action.prevention.length > 0) {
                detailedMsg += `🛡️ PREVENTION:\n`;
                action.prevention.forEach(step => {
                  detailedMsg += `  • ${step}\n`;
                });
                detailedMsg += `\n`;
              }

              if (idx < recommendations.actions.length - 1) {
                detailedMsg += `\n`;
              }
            });
          }

          // Display preventive actions if normal
          if (recommendations.preventive && recommendations.preventive.length > 0) {
            recommendations.preventive.forEach(prev => {
              detailedMsg += `${prev.icon} ${prev.title}\n`;
              prev.actions.forEach(action => {
                detailedMsg += `  • ${action}\n`;
              });
            });
          }

          detailedMsg += `\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
          
          // Add priority-based footer
          if (recommendations.priority === "critical") {
            detailedMsg += `🚨 CRITICAL: Follow these steps IMMEDIATELY to prevent failure!\n`;
          } else if (recommendations.priority === "high") {
            detailedMsg += `⚠️ URGENT: Address these issues within 1 hour to prevent escalation.\n`;
          } else if (recommendations.priority === "medium") {
            detailedMsg += `📋 IMPORTANT: Schedule these actions within 24 hours.\n`;
          } else {
            detailedMsg += `✅ HEALTHY: Your machine is in good condition. Continue monitoring.\n`;
          }
        }

        try {
          if (window.chatbot && typeof window.chatbot.say === "function") {
            window.chatbot.say(detailedMsg);
          }
        } catch (err) {
          console.warn("chatbot.say unavailable", err);
        }
      }
    } catch (err) {
      console.error("Error analyzing chart:", err);
      try {
        if (window.chatbot && typeof window.chatbot.say === "function") {
          window.chatbot.say("⚠️ Analysis failed. Please check if the backend server is running.");
        }
      } catch (e) {
        console.warn("chatbot error notification failed", e);
      }
    }
  };

  // ------------------------------------
  // LABELS FOR COLAB
  // ------------------------------------
  const generateLabels = (avg) => {
    const set = (v, low, high, crit) => (v >= crit ? "critical" : v > high ? "high" : v >= low ? "medium" : "low");

    return {
      temperature: set(avg.temperature ?? 0, 65, 75, 85),
      vibration: set(avg.vibration ?? 0, 3, 5, 7),
      speed: set(avg.speed ?? 0, 1150, 1250, 1350),
    };
  };

  // ------------------------------------
  // SEND TO COLAB / NGROK
  // ------------------------------------
  const handleSendToColab = async () => {
    if (!dashboardData) return;
    
    setEmailSent(true);
    
    try {
      const labels = generateLabels(averages);

      // Use local backend instead of ngrok
      const res = await axios.post("http://localhost:5000/process", {
        temperature: dashboardData.temperature,
        vibration: dashboardData.vibration,
        speed: dashboardData.speed,
        email: currentUser?.email,
        machine_id: selectedMachine,
        labels,
      });

      setReport(res.data);
      setAlerts(res.data.alerts || []);
      setShutdown(res.data.shutdown || false);
      
      // Update health summary with alert status
      let summary = res.data.recommendation || "Analysis complete";
      if (res.data.email_sent) {
        summary += " 📧 Alert email sent successfully!";
      }
      setHealthSummary(summary);

      // Show success message in chatbot if available
      if (window.chatbot) {
        const statusMsg = res.data.status === "CRITICAL" ? "🚨 CRITICAL" : 
                         res.data.status === "High Risk" ? "⚠️ HIGH RISK" :
                         res.data.status === "Moderate" ? "📋 MODERATE" : "✅ HEALTHY";
        window.chatbot.say(`${statusMsg} - Analysis complete. ${res.data.email_sent ? "Alert email sent!" : ""}`);
      }

      setTimeout(() => setEmailSent(false), 8000);
    } catch (err) {
      console.error("Analysis error", err);
      setHealthSummary("❌ Analysis failed. Please try again.");
      setEmailSent(false);
      
      if (window.chatbot) {
        window.chatbot.say("❌ Analysis failed. Please check your connection and try again.");
      }
    }
  };

  // -------------------------------
  // UI START
  // -------------------------------
  return (
    <div className="min-h-screen bg-gray-100 p-6" onDrop={onDrop} onDragOver={(e) => e.preventDefault()}>
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
        <select className="border rounded p-2 ml-2" value={selectedMachine} onChange={(e) => setSelectedMachine(e.target.value)}>
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
          <GaugeCard label="Temperature" value={averages.temperature ?? 0} />
        </Panel>

        <Panel title="Second">
          <GaugeCard label="Vibration" value={averages.vibration ?? 0} />
        </Panel>

        <Panel title="Third">
          <GaugeCard label="Speed (RPM)" value={averages.speed ?? 0} maxValue={2000} />
        </Panel>
      </div>

      {/* CHARTS */}
      {dashboardData && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="bg-white rounded-xl shadow-md p-4 cursor-grab hover:shadow-lg" draggable onDragStart={(e) => onDragStart(e, "lineChart")}>
              <canvas id="lineChart" style={{ width: "100%", height: "220px" }}></canvas>
            </div>

            <div className="bg-white rounded-xl shadow-md p-4 cursor-grab hover:shadow-lg" draggable onDragStart={(e) => onDragStart(e, "barChart")}>
              <canvas id="barChart" style={{ width: "100%", height: "220px" }}></canvas>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-4 mb-6 cursor-grab hover:shadow-lg flex items-center justify-center" draggable onDragStart={(e) => onDragStart(e, "pieChart")} style={{ minHeight: "280px" }}>
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
                const color = level === "critical" ? "bg-red-700 text-white" : level === "high" ? "bg-red-500 text-white" : level === "medium" ? "bg-yellow-400 text-black" : "bg-green-500 text-white";

                return (
                  <div key={key} className="p-4 bg-blue-50 rounded shadow">
                    <h4 className="font-bold text-blue-700">{key.toUpperCase()}</h4>
                    <p className="text-xl mt-2">{val ?? 0}</p>
                    <span className={`px-3 py-1 text-xs rounded-full mt-2 inline-block ${color}`}>{level.toUpperCase()}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* ANALYZE BUTTON */}
          <div className="text-center mb-6">
            <button onClick={handleSendToColab} disabled={emailSent} className={`px-6 py-2 text-white rounded-lg ${emailSent ? "bg-gray-400" : "bg-green-600 hover:bg-green-700"}`}>
              {emailSent ? "Analyzing..." : "Analyze"}
            </button>
          </div>

          {/* REPORT */}
          {report && (
            <div className="bg-white p-5 rounded shadow mb-6">
              <h3 className="font-semibold mb-4">Machine Status Report</h3>
              <p>
                <strong>Status:</strong> {report.status}
              </p>
              <p>
                <strong>Avg Temp:</strong> {report.avg_temp}
              </p>
              <p>
                <strong>Avg Vibration:</strong> {report.avg_vibration}
              </p>
              <p>
                <strong>Avg Speed:</strong> {report.avg_speed}
              </p>

              {report.report_url && (
                <button
                  className="px-4 py-2 bg-indigo-600 text-white rounded mt-4"
                  onClick={() => {
                    fetch(report.report_url, { method: "GET", headers: { "ngrok-skip-browser-warning": "true" } })
                      .then((response) => {
                        if (!response.ok) throw new Error("Failed downloading PDF");
                        return response.blob();
                      })
                      .then((blob) => {
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = "Machine_Report.pdf";
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
