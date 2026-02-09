import React from "react";

export default function Button({ variant = "solid", className = "", ...props }) {
  const variantClass =
    variant === "outline"
      ? "outline"
      : variant === "ghost"
        ? "ghost"
        : variant === "danger"
          ? "danger"
          : "";

  return (
    <button className={`btn ${variantClass} ${className}`.trim()} {...props} />
  );
}
