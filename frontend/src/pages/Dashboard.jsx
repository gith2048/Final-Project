import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import Chart from "chart.js/auto";
import ChartDataLabels from "chartjs-plugin-datalabels";
import axios from "axios";
import ChatWidget from "../pages/ChatWidget";
import RecommendationPanel from "../pages/RecommendationPanel";
import Panel from "../pages/Panel";
import GaugeCard from "../pages/GaugeCard";
import SliderControl from "../pages/SliderControl";
import ColorPickerCard from "../pages/ColorPickerCard";
import MachineForm from "../components/MachineForm";

Chart.register(ChartDataLabels);

const SEQ_LEN = 10; // LSTM sequence length (must match backend)

// Server Status Indicator Component
const ServerStatusIndicator = () => {
  const [serverStatus, setServerStatus] = useState('checking');
  
  useEffect(() => {
    const checkServerStatus = async () => {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000);
        
        const response = await fetch('http://localhost:5000/', { 
          method: 'GET',
          mode: 'cors',
          signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        setServerStatus(response.ok ? 'online' : 'offline');
      } catch (error) {
        setServerStatus('offline');
      }
    };
    
    checkServerStatus();
    const interval = setInterval(checkServerStatus, 10000); // Check every 10 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  const getStatusConfig = () => {
    switch (serverStatus) {
      case 'online':
        return {
          color: 'text-green-600',
          bg: 'bg-green-100',
          icon: '🟢',
          text: 'Server Online'
        };
      case 'offline':
        return {
          color: 'text-red-600',
          bg: 'bg-red-100',
          icon: '🔴',
          text: 'Server Offline'
        };
      default:
        return {
          color: 'text-yellow-600',
          bg: 'bg-yellow-100',
          icon: '🟡',
          text: 'Checking...'
        };
    }
  };
  
  const config = getStatusConfig();
  
  return (
    <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
      <span>{config.icon}</span>
      <span>{config.text}</span>
    </div>
  );
};

const Dashboard = () => {
  const navigate = useNavigate();
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
  const [selectedChartType, setSelectedChartType] = useState("line"); // New state for chart selection
  const [isDropdownOpen, setIsDropdownOpen] = useState(false); // State for dropdown visibility
  
  // New states for machine management
  const [userMachines, setUserMachines] = useState([]);
  const [showMachineForm, setShowMachineForm] = useState(false);
  const [loadingMachines, setLoadingMachines] = useState(false);

  const chatbotRef = useRef(null);
  const dropdownRef = useRef(null);

  const companyName = "TechNova Industries";
  const locationName = "Bangalore, India";

  // Handle back navigation
  const handleBack = () => {
    // Close the current tab and return to the previous tab (profile page)
    window.close();
    
    // Fallback: if window.close() doesn't work (some browsers restrict it),
    // navigate to profile page in the same tab
    setTimeout(() => {
      if (!window.closed) {
        navigate("/profile");
      }
    }, 100);
  };

  // Static machines for demo data (fallback)
  const staticMachines = [
    { id: 1, name: "Machine_A", displayName: "Machine1" },
    { id: 2, name: "Machine_B", displayName: "Machine2" },
    { id: 3, name: "Machine_C", displayName: "Machine3" },
  ];

  // Load logged user
  useEffect(() => {
    try {
      const savedUser = JSON.parse(localStorage.getItem("currentUser"));
      if (savedUser) {
        setCurrentUser(savedUser);
        loadUserMachines(savedUser.email);
      }
    } catch {
      setCurrentUser(null);
    }
  }, []);

  // Load user's machines
  const loadUserMachines = async (userEmail) => {
    if (!userEmail) return;
    
    setLoadingMachines(true);
    try {
      const response = await axios.get(`http://localhost:5000/api/machines?user_email=${encodeURIComponent(userEmail)}`);
      setUserMachines(response.data.machines || []);
    } catch (error) {
      console.error('Error loading user machines:', error);
      setUserMachines([]);
    } finally {
      setLoadingMachines(false);
    }
  };

  // Handle machine added
  const handleMachineAdded = (newMachine) => {
    // Refresh the machines list
    if (currentUser?.email) {
      loadUserMachines(currentUser.email);
    }
  };

  // Calculate next service date based on machine condition
  const calculateNextServiceDate = () => {
    if (!averages.temperature || !averages.vibration || !averages.speed) {
      return {
        date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // Default 30 days
        urgency: 'normal',
        reason: 'Standard maintenance schedule'
      };
    }

    const temp = averages.temperature;
    const vib = averages.vibration;
    const speed = averages.speed;

    let daysUntilService = 30; // Default 30 days
    let urgency = 'normal';
    let reason = 'Standard maintenance schedule';

    // Critical conditions - immediate service needed
    if (temp >= 85 || vib >= 7 || speed >= 1350) {
      daysUntilService = 1;
      urgency = 'critical';
      reason = 'Critical parameters detected - immediate service required';
    }
    // High risk conditions - service within 3-7 days
    else if (temp >= 75 || vib >= 5 || speed >= 1250) {
      daysUntilService = Math.random() < 0.5 ? 3 : 7;
      urgency = 'high';
      reason = 'High parameter levels - early service recommended';
    }
    // Medium risk conditions - service within 10-15 days
    else if (temp >= 65 || vib >= 3 || speed >= 1150) {
      daysUntilService = Math.floor(Math.random() * 6) + 10; // 10-15 days
      urgency = 'medium';
      reason = 'Elevated parameters - schedule service soon';
    }
    // Good conditions - standard 20-30 day schedule
    else {
      daysUntilService = Math.floor(Math.random() * 11) + 20; // 20-30 days
      urgency = 'normal';
      reason = 'Machine in good condition - standard schedule';
    }

    const serviceDate = new Date(Date.now() + daysUntilService * 24 * 60 * 60 * 1000);
    
    return {
      date: serviceDate,
      urgency,
      reason,
      daysUntil: daysUntilService
    };
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // -------------------------------
  // FETCH MACHINE DATA
  // -------------------------------
  useEffect(() => {
    if (!selectedMachine) return;

    const fetchData = async () => {
      try {
        const res = await axios.get("http://localhost:5000/api/sensor-data");
        
        // For user machines, try to find data by machine identifier
        // If not found, use static demo data for now
        let machineData = res.data[selectedMachine];
        
        // Fallback to static demo data if user machine data not found
        if (!machineData) {
          // Map user machine to demo data
          const demoMachineMap = {
            'Machine_1': 'Machine_A',
            'Machine_2': 'Machine_B', 
            'Machine_3': 'Machine_C'
          };
          
          const demoMachine = demoMachineMap[selectedMachine] || 'Machine_A';
          machineData = res.data[demoMachine];
        }

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

  // Force re-render of machine cards when averages change
  useEffect(() => {
    // This will trigger a re-render of the machine selection section
    // when averages are updated, ensuring health status reflects current data
  }, [averages]);

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
  // CALCULATE MACHINE HEALTH PERCENTAGE
  // -------------------------------
  const getMachineHealthPercentage = (machineName) => {
    // If we have real data for the selected machine, calculate based on actual values
    if (selectedMachine === machineName && averages.temperature && averages.vibration && averages.speed) {
      // Enhanced scoring system with more granular thresholds
      const tempScore = calculateParameterScore(averages.temperature, [
        { max: 60, score: 100 },
        { max: 70, score: 90 },
        { max: 75, score: 80 },
        { max: 80, score: 70 },
        { max: 85, score: 50 },
        { max: 90, score: 30 },
        { max: Infinity, score: 10 }
      ]);
      
      const vibScore = calculateParameterScore(averages.vibration, [
        { max: 2, score: 100 },
        { max: 3, score: 90 },
        { max: 4, score: 80 },
        { max: 5, score: 70 },
        { max: 6, score: 50 },
        { max: 7, score: 30 },
        { max: Infinity, score: 10 }
      ]);
      
      const speedScore = calculateParameterScore(averages.speed, [
        { max: 1100, score: 100 },
        { max: 1200, score: 90 },
        { max: 1250, score: 80 },
        { max: 1300, score: 70 },
        { max: 1350, score: 50 },
        { max: 1400, score: 30 },
        { max: Infinity, score: 10 }
      ]);

      // Add trend analysis if we have dashboard data
      let trendPenalty = 0;
      if (dashboardData && dashboardData.temperature.length >= 5) {
        trendPenalty = calculateTrendPenalty();
      }
      
      const baseScore = Math.round((tempScore + vibScore + speedScore) / 3);
      return Math.max(10, baseScore - trendPenalty); // Minimum 10% health
    }
    
    // For non-selected machines, use static values but make them more realistic
    const healthData = {
      'Machine_A': 85,
      'Machine_B': 72,
      'Machine_C': 94
    };
    return healthData[machineName] || 80;
  };

  // Helper function to calculate parameter score based on thresholds
  const calculateParameterScore = (value, thresholds) => {
    for (const threshold of thresholds) {
      if (value <= threshold.max) {
        return threshold.score;
      }
    }
    return 10; // Fallback minimum score
  };

  // Calculate trend penalty based on recent data trends
  const calculateTrendPenalty = () => {
    if (!dashboardData || dashboardData.temperature.length < 5) return 0;
    
    const recentCount = 5;
    const recentTemp = dashboardData.temperature.slice(-recentCount);
    const recentVib = dashboardData.vibration.slice(-recentCount);
    const recentSpeed = dashboardData.speed.slice(-recentCount);
    
    let penalty = 0;
    
    // Check for increasing temperature trend
    const tempTrend = calculateTrend(recentTemp);
    if (tempTrend > 2 && averages.temperature > 70) penalty += 5;
    
    // Check for increasing vibration trend
    const vibTrend = calculateTrend(recentVib);
    if (vibTrend > 0.5 && averages.vibration > 3) penalty += 5;
    
    // Check for erratic speed behavior
    const speedVariance = calculateVariance(recentSpeed);
    if (speedVariance > 10000) penalty += 3;
    
    return penalty;
  };

  // Calculate trend (positive = increasing, negative = decreasing)
  const calculateTrend = (data) => {
    if (data.length < 2) return 0;
    const first = data[0];
    const last = data[data.length - 1];
    return last - first;
  };

  // Calculate variance to detect erratic behavior
  const calculateVariance = (data) => {
    if (data.length < 2) return 0;
    const mean = data.reduce((sum, val) => sum + val, 0) / data.length;
    const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length;
    return variance;
  };

  // -------------------------------
  // GET HEALTH STATUS TEXT
  // -------------------------------
  const getHealthStatusText = (percentage, machineName) => {
    // For selected machine with real data, use more detailed status
    if (selectedMachine === machineName && averages.temperature && averages.vibration && averages.speed) {
      if (percentage >= 90) return 'Excellent';
      if (percentage >= 80) return 'Healthy';
      if (percentage >= 70) return 'Good';
      if (percentage >= 60) return 'Fair';
      if (percentage >= 50) return 'Poor';
      if (percentage >= 30) return 'Risky';
      return 'Critical';
    }
    
    // For non-selected machines, use simpler status
    if (percentage >= 80) return 'Healthy';
    if (percentage >= 60) return 'Medium';
    if (percentage >= 40) return 'Risky';
    return 'Critical';
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

    // LINE: Temp + Vibration (conditional)
    if (selectedChartType === "line") {
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
    }

    // BAR: Speed (conditional)
    if (selectedChartType === "bar") {
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
    }

    // PIE: Load Estimate (conditional)
    if (selectedChartType === "pie") {
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
    }

    setCharts(newCharts);
  };

  useEffect(() => {
    if (dashboardData) {
      // Small delay to ensure DOM elements are rendered
      setTimeout(() => renderCharts(), 100);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dashboardData, selectedChartType]);

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
          detailedMsg += `• Temperature: ${lstm.forecast.temperature.toFixed(2)}°C\n`;
          detailedMsg += `• Vibration: ${lstm.forecast.vibration.toFixed(2)} mm/s\n`;
          detailedMsg += `• Speed: ${lstm.forecast.speed.toFixed(2)} RPM\n\n`;
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
      {/* HEADER SECTION */}
      <div className="mb-8">
        {/* Back Button */}
        <div className="mb-4">
          {/* <button
            onClick={handleBack}
            className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors border border-gray-300"
            title="Go Back"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </button> */}
        </div>

        {/* Title with Gear Icons */}
        <div className="flex items-center gap-3 mb-6">
          <div className="flex items-center">
            <svg className="w-8 h-8 text-cyan-400" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 15.5A3.5 3.5 0 0 1 8.5 12A3.5 3.5 0 0 1 12 8.5a3.5 3.5 0 0 1 3.5 3.5a3.5 3.5 0 0 1-3.5 3.5m7.43-2.53c.04-.32.07-.64.07-.97c0-.33-.03-.66-.07-1l2.11-1.63c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.31-.61-.22l-2.49 1c-.52-.39-1.06-.73-1.69-.98l-.37-2.65A.506.506 0 0 0 14 2h-4c-.25 0-.46.18-.5.42l-.37 2.65c-.63.25-1.17.59-1.69.98l-2.49-1c-.22-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64L4.57 11c-.04.34-.07.67-.07 1c0 .33.03.65.07.97L2.46 14.6c-.19.15-.24.42-.12.64l2 3.46c.12.22.39.31.61.22l2.49-1c.52.39 1.06.73 1.69.98l.37 2.65c.04.24.25.42.5.42h4c.25 0 .46-.18.5-.42l.37-2.65c.63-.25 1.17-.59 1.69-.98l2.49 1c.22.09.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.66Z"/>
            </svg>
            <svg className="w-6 h-6 text-cyan-300 -ml-2" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 15.5A3.5 3.5 0 0 1 8.5 12A3.5 3.5 0 0 1 12 8.5a3.5 3.5 0 0 1 3.5 3.5a3.5 3.5 0 0 1-3.5 3.5m7.43-2.53c.04-.32.07-.64.07-.97c0-.33-.03-.66-.07-1l2.11-1.63c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.31-.61-.22l-2.49 1c-.52-.39-1.06-.73-1.69-.98l-.37-2.65A.506.506 0 0 0 14 2h-4c-.25 0-.46.18-.5.42l-.37 2.65c-.63.25-1.17.59-1.69.98l-2.49-1c-.22-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64L4.57 11c-.04.34-.07.67-.07 1c0 .33.03.65.07.97L2.46 14.6c-.19.15-.24.42-.12.64l2 3.46c.12.22.39.31.61.22l2.49-1c.52.39 1.06.73 1.69.98l.37 2.65c.04.24.25.42.5.42h4c.25 0 .46-.18.5-.42l.37-2.65c.63-.25 1.17-.59 1.69-.98l2.49 1c.22.09.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.66Z"/>
            </svg>
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-800">Machine Health Monitoring Dashboard</h1>
            <h2 className="text-2xl font-bold text-gray-800"> </h2>
          </div>
        </div>
      </div>

      {/* MACHINE SELECTOR */}
      <div className="mb-8 w-full">
        {loadingMachines ? (
          <div className="flex justify-center items-center py-12">
            <div className="flex items-center space-x-3">
              <svg className="animate-spin w-6 h-6 text-cyan-500" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-gray-600">Loading your machines...</span>
            </div>
          </div>
        ) : userMachines.length === 0 ? (
          // Show only Add Machine button when no machines
          <div className="flex justify-center">
            <div className="bg-white rounded-2xl p-8 shadow-lg border-2 border-dashed border-gray-300 hover:border-cyan-400 transition-all duration-300 max-w-md w-full">
              <div className="text-center">
                <div className="w-16 h-16 bg-cyan-400 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">Add Your First Machine</h3>
                <p className="text-gray-600 mb-6">Get started by adding a machine to monitor its health and performance</p>
                <button
                  onClick={() => setShowMachineForm(true)}
                  className="w-full py-3 px-6 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl font-semibold hover:from-cyan-600 hover:to-blue-700 transition-all duration-200"
                >
                  Add Machine
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-between gap-8 w-full px-8">
            {/* User's Machine Cards */}
            {userMachines.map((machine) => {
              const getHealthColor = (percentage) => {
                if (percentage >= 80) return 'stroke-green-500';
                if (percentage >= 60) return 'stroke-yellow-500';
                return 'stroke-red-500';
              };

              const getHealthBgColor = (percentage) => {
                if (percentage >= 80) return 'text-green-600';
                if (percentage >= 60) return 'text-yellow-600';
                return 'text-red-600';
              };

              // Use machine ID as identifier for user machines
              const machineIdentifier = `Machine_${machine.id}`;
              const healthPercentage = getMachineHealthPercentage(machineIdentifier);
              const healthColor = getHealthColor(healthPercentage);
              const healthTextColor = getHealthBgColor(healthPercentage);
              const healthStatusText = getHealthStatusText(healthPercentage, machineIdentifier);
              const isSelected = selectedMachine === machineIdentifier;

              return (
                <div 
                  key={machine.id} 
                  className={`bg-white rounded-2xl p-6 shadow-lg border-2 transition-all duration-300 ${
                    isSelected 
                      ? 'border-green-400 bg-green-50 shadow-xl transform scale-105' 
                      : 'border-gray-200 hover:border-gray-300 hover:shadow-xl'
                  } flex-1 min-w-0 mx-2`}
                >
                  {/* Machine Name */}
                  <h3 className="text-base font-bold text-gray-800 mb-1 text-center">
                    {machine.name}
                  </h3>
                  <p className="text-xs text-gray-500 mb-3 text-center">
                    {machine.motor_type} • {machine.motor_id}
                  </p>

                {/* Health Circle */}
                <div className="flex justify-center mb-4">
                  <div className="relative w-24 h-24">
                    <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 36 36">
                      {/* Background circle */}
                      <path
                        className="stroke-gray-200"
                        strokeWidth="2.5"
                        fill="transparent"
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                      {/* Progress circle */}
                      <path
                        className={healthColor}
                        strokeWidth="2.5"
                        fill="transparent"
                        strokeDasharray={`${healthPercentage}, 100`}
                        d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      />
                    </svg>
                    {/* Center content */}
                    <div className="absolute inset-0 flex items-center justify-center px-1">
                      <span className={`text-xs font-bold text-center leading-tight ${healthTextColor}`}>
                        {healthStatusText}
                      </span>
                    </div>
                  </div>
                </div>

                  {/* Select Button */}
                  <button
                    onClick={() => setSelectedMachine(isSelected ? "" : machineIdentifier)}
                    title={isSelected ? "Click to deselect this machine" : "Click to select this machine"}
                    className={`w-full py-2 px-3 rounded-xl font-semibold text-sm transition-all duration-200 ${
                      isSelected 
                        ? 'bg-green-500 text-white shadow-lg border-2 border-green-600 hover:bg-green-600' 
                        : 'bg-cyan-400 text-white hover:bg-cyan-500 hover:shadow-md'
                    }`}
                  >
                    {isSelected ? (
                      <div className="flex items-center justify-center space-x-1">
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span>Selected</span>
                      </div>
                    ) : (
                      'Select'
                    )}
                  </button>
                </div>
              );
            })}

            {/* Add Machine Card */}
            <div className="bg-white rounded-2xl p-6 shadow-lg border-2 border-dashed border-gray-300 hover:border-gray-400 transition-all duration-300 flex-1 min-w-0 mx-2 flex flex-col items-center justify-center">
              <button
                onClick={() => setShowMachineForm(true)}
                className="w-full h-full flex flex-col items-center justify-center py-4 text-gray-600 hover:text-gray-800 transition-colors"
              >
                <div className="w-12 h-12 bg-cyan-400 rounded-full flex items-center justify-center mb-2">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </div>
                <span className="text-base font-semibold">Add Machine</span>
              </button>
            </div>
          </div>
        )}

        {/* Selected Machine Info */}
        {/* {selectedMachine && userMachines.length > 0 && (
          <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border-2 border-green-200 shadow-md">
            <div className="flex items-center space-x-2">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-green-800 font-medium">
                <span className="font-semibold">Currently Selected:</span> {
                  (() => {
                    const machineId = selectedMachine.replace('Machine_', '');
                    const machine = userMachines.find(m => m.id.toString() === machineId);
                    return machine ? machine.name : selectedMachine;
                  })()
                }
              </p>
            </div>
          </div>
        )} */}
      </div>

      {/* PANELS - Only show when machine is selected */}
      {selectedMachine && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <GaugeCard 
            label="Temperature" 
            value={averages.temperature ?? 0} 
            unit="°C" 
            maxValue={100} 
          />
          <GaugeCard 
            label="Vibration" 
            value={averages.vibration ?? 0} 
            unit="mm/s" 
            maxValue={10} 
          />
          <GaugeCard 
            label="Speed" 
            value={averages.speed ?? 0} 
            unit="RPM" 
            maxValue={2000} 
          />
        </div>
      )}

      {/* CHARTS CONTAINER - Only show when machine is selected */}
      {selectedMachine && dashboardData && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          {/* Chart Header with Selection Dropdown */}
          <div className="flex items-center justify-between mb-6 pb-4 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <svg className="w-6 h-6 text-cyan-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <h2 className="text-2xl font-bold text-gray-800">Machine Analytics Dashboard</h2>
            </div>
            
            {/* Chart Selection Dropdown */}
            <div className="relative" ref={dropdownRef}>
              <button
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className="bg-white border border-gray-300 rounded-lg px-4 py-2.5 text-left shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition-all duration-200 min-w-[200px]"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-base">
                      {selectedChartType === "line" && "📈"}
                      {selectedChartType === "bar" && "📊"}
                      {selectedChartType === "pie" && "🥧"}
                    </span>
                    <span className="font-medium text-gray-900 text-sm">
                      {selectedChartType === "line" && "Temperature & Vibration"}
                      {selectedChartType === "bar" && "Speed Chart"}
                      {selectedChartType === "pie" && "Load Distribution"}
                    </span>
                  </div>
                  <svg 
                    className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`} 
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </button>

              {/* Dropdown Options */}
              {isDropdownOpen && (
                <div className="absolute z-20 right-0 mt-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg">
                  {[
                    { value: "line", label: "Temperature & Vibration", icon: "📈", desc: "Line chart analysis" },
                    { value: "bar", label: "Speed Chart", icon: "📊", desc: "Bar chart visualization" },
                    { value: "pie", label: "Load Distribution", icon: "🥧", desc: "Pie chart breakdown" }
                  ].map((option) => (
                    <button
                      key={option.value}
                      onClick={() => {
                        setSelectedChartType(option.value);
                        setIsDropdownOpen(false);
                      }}
                      className={`w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors duration-150 first:rounded-t-lg last:rounded-b-lg ${
                        selectedChartType === option.value ? 'bg-cyan-50 text-cyan-700' : 'text-gray-700'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-lg">{option.icon}</span>
                        <div className="flex-1">
                          <div className="font-medium">{option.label}</div>
                          <div className="text-xs text-gray-500">{option.desc}</div>
                        </div>
                        {selectedChartType === option.value && (
                          <svg className="w-4 h-4 text-cyan-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Charts Display Area */}
          <div className="w-full">
            {/* Conditional Chart Rendering */}
            {(selectedChartType === "line" || selectedChartType === "bar") && (
              <div className="grid gap-6 mb-6 grid-cols-1">
                {selectedChartType === "line" && (
                  <div className="bg-gray-50 rounded-xl shadow-sm p-6 cursor-grab hover:shadow-md border border-gray-200 transition-all duration-200" draggable onDragStart={(e) => onDragStart(e, "lineChart")}>
                    <div className="flex items-center gap-2 mb-4">
                      <span className="text-lg">📈</span>
                      <h4 className="text-lg font-semibold text-gray-800">Temperature & Vibration</h4>
                    </div>
                    <div className="relative" style={{ height: "400px" }}>
                      <canvas id="lineChart" style={{ width: "100%", height: "100%" }}></canvas>
                    </div>
                  </div>
                )}

                {selectedChartType === "bar" && (
                  <div className="bg-gray-50 rounded-xl shadow-sm p-6 cursor-grab hover:shadow-md border border-gray-200 transition-all duration-200" draggable onDragStart={(e) => onDragStart(e, "barChart")}>
                    <div className="flex items-center gap-2 mb-4">
                      <span className="text-lg">📊</span>
                      <h4 className="text-lg font-semibold text-gray-800">Speed (RPM)</h4>
                    </div>
                    <div className="relative" style={{ height: "400px" }}>
                      <canvas id="barChart" style={{ width: "100%", height: "100%" }}></canvas>
                    </div>
                  </div>
                )}
              </div>
            )}

            {selectedChartType === "pie" && (
              <div className="bg-gray-50 rounded-xl shadow-sm p-6 cursor-grab hover:shadow-md border border-gray-200 transition-all duration-200">
                <div className="flex items-center gap-2 mb-4">
                  <span className="text-lg">🥧</span>
                  <h4 className="text-lg font-semibold text-gray-800">Load Distribution</h4>
                </div>
                <div className="flex justify-center">
                  <div style={{ width: "400px", height: "400px" }}>
                    <canvas id="pieChart" style={{ width: "100%", height: "100%" }}></canvas>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* AVERAGES */}
      {/* {dashboardData && (
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
      )} */}

      {/* ANALYZE SECTION - Only show when machine is selected */}
      {selectedMachine && dashboardData && (
        <>
          {/* Modern Analyze Button and Service Date */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8 max-w-7xl mx-auto px-4">
            {/* AI Analysis Card */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 w-full modern-card animate-fade-in-up">
              <div className="text-center">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-3">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-1">AI-Powered Analysis</h3>
                <p className="text-sm text-gray-600 mb-4">Get intelligent insights and recommendations for your machine</p>
                
                <button 
                  onClick={handleSendToColab} 
                  disabled={emailSent} 
                  className={`w-full py-3 px-5 rounded-xl font-semibold text-base transition-all duration-300 transform ${
                    emailSent 
                      ? "bg-gray-100 text-gray-400 cursor-not-allowed" 
                      : "bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 hover:scale-105 shadow-lg hover:shadow-xl animate-pulse-glow"
                  }`}
                >
                  {emailSent ? (
                    <div className="flex items-center justify-center space-x-2">
                      <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <span>Analyzing...</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center space-x-2">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                      <span>Start Analysis</span>
                    </div>
                  )}
                </button>

                {emailSent && (
                  <div className="mt-3 flex items-center justify-center space-x-2 text-xs text-gray-500">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse"></div>
                    <span>Processing machine data with AI models...</span>
                  </div>
                )}

                {/* Analysis Features */}
                <div className="mt-4 space-y-3">
                  <div className="bg-blue-50 rounded-lg p-3">
                    <div className="flex items-start space-x-2">
                      <svg className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div className="text-left">
                        <p className="text-xs font-semibold text-blue-900">AI Models Used</p>
                        <p className="text-xs text-blue-700">Random Forest • Isolation Forest • LSTM</p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-purple-50 rounded-lg p-3">
                    <div className="flex items-start space-x-2">
                      <svg className="w-4 h-4 text-purple-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div className="text-left">
                        <p className="text-xs font-semibold text-purple-900">Analysis Includes</p>
                        <p className="text-xs text-purple-700">Failure prediction • Anomaly detection • Forecasting</p>
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button 
                      className="flex-1 py-2 px-3 rounded-lg text-xs font-semibold transition-all duration-200 bg-gray-100 text-gray-700 hover:bg-gray-200"
                      onClick={() => {
                        const info = `Current Machine Status:\n\nTemperature: ${averages.temperature.toFixed(2)}°C\nVibration: ${averages.vibration.toFixed(2)} mm/s\nSpeed: ${averages.speed.toFixed(2)} RPM\n\nHealth Summary:\n${healthSummary}`;
                        navigator.clipboard.writeText(info);
                        alert('Machine status copied to clipboard!');
                      }}
                      title="Copy current status"
                    >
                      <div className="flex items-center justify-center space-x-1">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                        <span>Copy Status</span>
                      </div>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Next Service Date Card */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-6 w-full modern-card animate-fade-in-up">
              <div className="text-center">
                {(() => {
                  const serviceInfo = calculateNextServiceDate();
                  const urgencyConfig = {
                    critical: {
                      color: 'from-red-500 to-red-600',
                      textColor: 'text-red-700',
                      bgColor: 'bg-red-50',
                      icon: '🚨',
                      label: 'URGENT'
                    },
                    high: {
                      color: 'from-orange-500 to-red-500',
                      textColor: 'text-orange-700',
                      bgColor: 'bg-orange-50',
                      icon: '⚠️',
                      label: 'HIGH PRIORITY'
                    },
                    medium: {
                      color: 'from-yellow-500 to-orange-500',
                      textColor: 'text-yellow-700',
                      bgColor: 'bg-yellow-50',
                      icon: '📋',
                      label: 'SCHEDULED'
                    },
                    normal: {
                      color: 'from-green-500 to-emerald-600',
                      textColor: 'text-green-700',
                      bgColor: 'bg-green-50',
                      icon: '✅',
                      label: 'ROUTINE'
                    }
                  };

                  const config = urgencyConfig[serviceInfo.urgency];

                  return (
                    <>
                      <div className={`w-14 h-14 bg-gradient-to-br ${config.color} rounded-2xl flex items-center justify-center mx-auto mb-3`}>
                        <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                      
                      <h3 className="text-lg font-bold text-gray-900 mb-1">Next Service Date</h3>
                      <p className="text-sm text-gray-600 mb-3">Based on current machine condition</p>
                      
                      {/* Service Date Display */}
                      <div className={`${config.bgColor} rounded-xl p-4 mb-3`}>
                        <div className="flex items-center justify-center space-x-2 mb-2">
                          <span className="text-xl">{config.icon}</span>
                          <span className={`text-xs font-bold ${config.textColor} uppercase tracking-wider`}>
                            {config.label}
                          </span>
                        </div>
                        
                        <div className="text-2xl font-bold text-gray-900 mb-1">
                          {serviceInfo.date.toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric', 
                            year: 'numeric' 
                          })}
                        </div>
                        
                        <div className={`text-sm font-semibold ${config.textColor}`}>
                          {serviceInfo.daysUntil === 1 
                            ? 'Tomorrow' 
                            : `In ${serviceInfo.daysUntil} days`}
                        </div>
                      </div>

                      {/* Reason */}
                      <div className="bg-gray-50 rounded-lg p-3 mb-3">
                        <div className="flex items-start space-x-2">
                          <svg className="w-5 h-5 text-gray-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <p className="text-sm text-gray-600 text-left">
                            {serviceInfo.reason}
                          </p>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-2">
                        <button 
                          className={`flex-1 py-3 px-4 rounded-xl font-semibold text-sm transition-all duration-200 bg-gradient-to-r ${config.color} text-white hover:shadow-lg`}
                          onClick={() => {
                            alert(`Service scheduled for ${serviceInfo.date.toLocaleDateString()}\n\nReason: ${serviceInfo.reason}`);
                          }}
                        >
                          Schedule Service
                        </button>
                        <button 
                          className="px-4 py-3 rounded-xl font-semibold text-sm transition-all duration-200 bg-gray-100 text-gray-700 hover:bg-gray-200"
                          onClick={() => {
                            const details = `Next Service Date: ${serviceInfo.date.toLocaleDateString()}\nDays Until Service: ${serviceInfo.daysUntil}\nUrgency: ${config.label}\nReason: ${serviceInfo.reason}\n\nCurrent Readings:\nTemperature: ${averages.temperature.toFixed(2)}°C\nVibration: ${averages.vibration.toFixed(2)} mm/s\nSpeed: ${averages.speed.toFixed(2)} RPM`;
                            navigator.clipboard.writeText(details);
                            alert('Service details copied to clipboard!');
                          }}
                          title="Copy service details"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                        </button>
                      </div>
                    </>
                  );
                })()}
              </div>
            </div>
          </div>

          {/* MODERN REPORT SECTION */}
          {report && (
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden mb-8 modern-card animate-slide-in-right">
              {/* Report Header */}
              <div className="bg-gradient-to-r from-indigo-600 to-blue-600 px-8 py-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                      <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-white">Machine Status Report</h2>
                      <p className="text-indigo-100">Comprehensive analysis results</p>
                    </div>
                  </div>
                  <div className={`px-4 py-2 rounded-full text-sm font-semibold ${
                    report.status === "CRITICAL" ? "bg-red-100 text-red-800" :
                    report.status === "High Risk" ? "bg-orange-100 text-orange-800" :
                    report.status === "Moderate" ? "bg-yellow-100 text-yellow-800" :
                    "bg-green-100 text-green-800"
                  }`}>
                    {report.status}
                  </div>
                </div>
              </div>

              {/* Report Content */}
              <div className="p-8">
                {/* Status Message */}
                <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <p className="text-blue-800 text-sm">
                        <strong>Report Status:</strong> Analysis complete. PDF report has been generated and is ready for download.
                      </p>
                    </div>
                    <ServerStatusIndicator />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  {[
                    { 
                      label: "Average Temperature", 
                      value: report.avg_temp, 
                      unit: "°C",
                      icon: "🌡️",
                      color: "text-red-600",
                      bgColor: "bg-red-50"
                    },
                    { 
                      label: "Average Vibration", 
                      value: report.avg_vibration, 
                      unit: "mm/s",
                      icon: "📳",
                      color: "text-blue-600",
                      bgColor: "bg-blue-50"
                    },
                    { 
                      label: "Average Speed", 
                      value: report.avg_speed, 
                      unit: "RPM",
                      icon: "⚡",
                      color: "text-green-600",
                      bgColor: "bg-green-50"
                    }
                  ].map((metric, index) => (
                    <div key={index} className={`${metric.bgColor} rounded-xl p-6 border border-gray-200`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-600">{metric.label}</span>
                        <span className="text-2xl">{metric.icon}</span>
                      </div>
                      <div className={`text-2xl font-bold ${metric.color}`}>
                        {Number(metric.value).toFixed(2)} <span className="text-lg font-normal">{metric.unit}</span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Download Report Button */}
                {report.report_url && (
                  <div className="flex justify-center space-x-4">
                    {/* Simple Direct Download Button */}
                    <button
                      className="flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-indigo-600 to-blue-600 text-white rounded-xl font-semibold hover:from-indigo-700 hover:to-blue-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                      onClick={() => {
                        const downloadUrl = `http://localhost:5000${report.report_url}`;
                        
                        // Simple direct download approach
                        const link = document.createElement('a');
                        link.href = downloadUrl;
                        link.download = 'Machine_Report.pdf';
                        link.target = '_blank';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        
                        // Show success message
                        if (window.chatbot && typeof window.chatbot.say === "function") {
                          window.chatbot.say("✅ Download initiated! Check your downloads folder.");
                        }
                      }}
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <span>Download PDF Report</span>
                    </button>
                    
                    {/* Alternative: View in Browser Button */}
                    <button
                      className="flex items-center space-x-3 px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-semibold hover:from-green-700 hover:to-emerald-700 transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-xl"
                      onClick={() => {
                        const downloadUrl = `http://localhost:5000${report.report_url}`;
                        
                        // Open PDF in new tab
                        const newWindow = window.open(downloadUrl, '_blank');
                        
                        // Check if popup was blocked
                        if (!newWindow || newWindow.closed || typeof newWindow.closed == 'undefined') {
                          alert("❌ Popup blocked. Please allow popups for this site and try again, or use the Download button instead.");
                        } else {
                          if (window.chatbot && typeof window.chatbot.say === "function") {
                            window.chatbot.say("✅ PDF opened in new tab!");
                          }
                        }
                      }}
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      <span>View PDF</span>
                    </button>
                  </div>
                )}

                {/* Troubleshooting Help */}
                {/* {report.report_url && (
                  <div className="mt-4 p-3 bg-gray-50 border border-gray-200 rounded-lg">
                    <details className="cursor-pointer">
                      <summary className="text-sm font-medium text-gray-700 hover:text-gray-900">
                        📋 Having trouble downloading? Click here for help
                      </summary>
                      <div className="mt-2 text-xs text-gray-600 space-y-2">
                        <div>
                          <p className="font-medium text-gray-700">🔧 Quick Fixes:</p>
                          <p>• Try the "View PDF" button to open in a new tab</p>
                          <p>• Check if your browser is blocking downloads or popups</p>
                          <p>• Refresh the page and try again</p>
                        </div>
                        <div>
                          <p className="font-medium text-gray-700">🖥️ Server Issues:</p>
                          <p>• Check the server status indicator above (should be 🟢 Online)</p>
                          <p>• If server is offline, start it by running: <code className="bg-gray-200 px-1 rounded">python app.py</code> in the backend folder</p>
                          <p>• Ensure the server is accessible at http://localhost:5000</p>
                        </div>
                        <div>
                          <p className="font-medium text-gray-700">🐛 Still having issues?</p>
                          <p>• Verify that the analyze button was clicked first to generate the report</p>
                          <p>• Try restarting both frontend and backend servers</p>
                          <p>• Check the browser console (F12) for error messages</p>
                        </div>
                      </div>
                    </details>
                  </div>
                )} */}
              </div>
            </div>
          )}

          {/* MODERN HEALTH SUMMARY */}
          {healthSummary && !recommendation && (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden mb-8 modern-card animate-fade-in-up">
              <div className="bg-gradient-to-r from-amber-500 to-orange-500 px-6 py-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">System Health Summary</h3>
                    <p className="text-amber-100 text-sm">Real-time machine condition assessment</p>
                  </div>
                </div>
              </div>
              <div className="p-6">
                <div className="prose prose-sm max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-line">{healthSummary}</p>
                </div>
              </div>
            </div>
          )}
        </>
      )}

      {recommendation && <RecommendationPanel data={recommendation} />}
      
      {/* Only show ChatWidget when machine is selected */}
      {selectedMachine && <ChatWidget chartData={dashboardData} />}
      
      {/* Machine Form Modal */}
      {showMachineForm && (
        <MachineForm
          onClose={() => setShowMachineForm(false)}
          onMachineAdded={handleMachineAdded}
          userEmail={currentUser?.email}
        />
      )}
    </div>
  );
};

export default Dashboard;
