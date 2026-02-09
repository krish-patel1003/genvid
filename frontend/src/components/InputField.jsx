import React from "react";

export default function InputField({ label, className = "", ...props }) {
  return (
    <label className={`field ${className}`.trim()}>
      <span className="field-label">{label}</span>
      <input {...props} />
    </label>
  );
}
