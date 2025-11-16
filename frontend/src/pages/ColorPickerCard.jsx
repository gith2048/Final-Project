import React, { useState } from "react";
import { ChromePicker } from "react-color";

const ColorPickerCard = ({ onChange }) => {
  const [color, setColor] = useState("#e62117");

  const handleChange = (c) => {
    setColor(c.hex);
    onChange?.(c.hex);
  };

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">Pick a Color</label>
      <ChromePicker color={color} onChangeComplete={handleChange} />
      <p className="mt-2 text-sm text-gray-600">Selected: {color}</p>
    </div>
  );
};

export default ColorPickerCard;