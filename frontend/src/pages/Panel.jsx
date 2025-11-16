import React from "react";

const Panel = ({ title, children }) => (
  <div className="bg-white rounded-xl shadow-md p-4 border border-gray-200">
    <h3 className="text-lg font-semibold text-gray-800 mb-3">{title}</h3>
    <div className="space-y-4">{children}</div>
  </div>
);

export default Panel;