import React from "react";

export default function Toast({ message, tone = "default" }) {
  if (!message) return null;
  return <div className={`toast ${tone === "error" ? "error" : ""}`.trim()}>{message}</div>;
}
