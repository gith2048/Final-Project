import React from "react";
import { Line, Pie, Bar } from "react-chartjs-2";
import { Chart as ChartJS, ArcElement, LineElement, BarElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend } from "chart.js";

ChartJS.register(ArcElement, LineElement, BarElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend);

const ChartCard = ({ type, data }) => {
  if (!data || !data[type]) return null;

  const chartProps = {
    data: data[type],
    options: { responsive: true, maintainAspectRatio: false },
    height: 200,
  };

  return (
    <div className="bg-gray-50 p-3 rounded-lg shadow-inner h-64">
      {type === "line" && <Line {...chartProps} />}
      {type === "pie" && <Pie {...chartProps} />}
      {type === "bar" && <Bar {...chartProps} />}
    </div>
  );
};

export default ChartCard;