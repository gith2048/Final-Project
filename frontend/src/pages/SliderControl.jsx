import React, { useState } from "react";
import Slider from "@mui/material/Slider";

const SliderControl = ({ label, value, onChange }) => {
  const [val, setVal] = useState(value);

  const handleChange = (e, newVal) => {
    setVal(newVal);
    onChange?.(newVal);
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <Slider
        value={val}
        onChange={handleChange}
        aria-label={label}
        valueLabelDisplay="auto"
        min={0}
        max={100}
      />
    </div>
  );
};

export default SliderControl;