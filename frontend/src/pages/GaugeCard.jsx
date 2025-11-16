import React from "react";
import GaugeChart from "react-gauge-chart";

const GaugeCard = ({ label, value }) => (
  <div className="text-center">
    <h4 className="text-sm font-medium text-gray-600 mb-2">{label}</h4>
    <GaugeChart
      id={`gauge-${label}`}
      nrOfLevels={20}
      percent={value / 100}
      colors={["#FF5F6D", "#FFC371"]}
      arcWidth={0.3}
      textColor="#333"
    />
    <p className="text-sm mt-2 text-gray-500">{value} %</p>
  </div>
);

export default GaugeCard;