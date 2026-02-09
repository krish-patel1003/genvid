import React from "react";

export default function TextAreaField({ label, className = "", ...props }) {
  return (
    <label className={`field ${className}`.trim()}>
      <span className="field-label">{label}</span>
      <textarea {...props} />
    </label>
  );
}
