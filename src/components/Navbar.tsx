import React from "react";

function BarsIcon() {
  return (
    <svg className="bars-icon" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect x="2" y="18" width="6" height="12" rx="2" fill="#a3e635" />
      <rect x="13" y="10" width="6" height="20" rx="2" fill="#a3e635" />
      <rect x="24" y="2" width="6" height="28" rx="2" fill="#a3e635" />
    </svg>
  );
}

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="container" style={{ justifyContent: "center", gap: 8 }}>
        <BarsIcon />
        <span style={{ fontFamily: "var(--font-poppins)", fontWeight: 800, fontSize: "1.35rem" }}>
          SMATCH <span className="neon-text">AI</span>
        </span>
        <span style={{ fontSize: "0.82rem", color: "#666", marginLeft: 8 }}>Resume-to-Job Matcher</span>
      </div>
    </nav>
  );
}