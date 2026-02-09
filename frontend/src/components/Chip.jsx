import React from "react";

export default function Chip({ children, className = "" }) {
  return <span className={`chip ${className}`.trim()}>{children}</span>;
}
