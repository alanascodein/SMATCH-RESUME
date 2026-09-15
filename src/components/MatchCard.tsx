import React, { useState } from "react";
import type { MatchResult } from "../types";
import { ChevronDown, ChevronUp, ExternalLink } from "lucide-react";

function SubBar({ label, value }: { label: string; value: number }) {
  const color = value >= 70 ? "#a3e635" : value >= 40 ? "#f59e0b" : "#f43f5e";
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.8rem", marginBottom: 3 }}>
        <span style={{ color: "#999", textTransform: "capitalize" }}>{label}</span>
        <span style={{ color, fontWeight: 700 }}>{value}</span>
      </div>
      <div style={{ height: 6, background: "#ffffff12", borderRadius: 3, overflow: "hidden" }}>
        <div style={{ width: `${value}%`, height: "100%", background: color, borderRadius: 3, transition: "width 0.4s ease" }} />
      </div>
    </div>
  );
}

function ReqRow({ r }: { r: any }) {
  const statusColor =
    r.status === "matched" ? "#a3e635" : r.status === "partial" ? "#f59e0b" : "#f43f5e";
  return (
    <div className="req-row">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: "0.85rem", fontWeight: 600, marginBottom: 4 }}>
            {r.text.length > 100 ? r.text.slice(0, 100) + "…" : r.text}
          </div>
          <div style={{ fontSize: "0.78rem", color: "#888" }}>{r.label}</div>
        </div>
        <span
          style={{
            fontSize: "0.78rem",
            fontWeight: 700,
            padding: "2px 10px",
            borderRadius: 6,
            background: `${statusColor}18`,
            color: statusColor,
            whiteSpace: "nowrap",
          }}
        >
          {r.score}%
        </span>
      </div>
      {r.evidence_text && (
        <div style={{ marginTop: 6, fontSize: "0.8rem", color: "#aaa", lineHeight: 1.5 }}>
          <span style={{ color: "#777", fontSize: "0.75rem" }}>EVIDENCE: </span>
          {r.evidence_text.length > 180 ? r.evidence_text.slice(0, 180) + "…" : r.evidence_text}
        </div>
      )}
      {r.reason && (
        <div style={{ marginTop: 4, fontSize: "0.78rem", color: "#a3e635aa", fontStyle: "italic" }}>
          {r.reason}
        </div>
      )}
    </div>
  );
}

function BucketBadge({ bucket, score }: { bucket: string; score: number }) {
  const colors: Record<string, string> = {
    Excellent: "#a3e635",
    Strong: "#22c55e",
    Potential: "#f59e0b",
    Low: "#f43f5e",
  };
  const c = colors[bucket] || "#888";
  return (
    <span
      style={{
        padding: "4px 14px",
        borderRadius: 8,
        background: `${c}18`,
        color: c,
        fontWeight: 700,
        fontSize: "0.85rem",
        letterSpacing: "-0.01em",
      }}
    >
      {bucket} · {score}/100
    </span>
  );
}

export default function MatchCard({ match }: { match: MatchResult }) {
  const [open, setOpen] = useState(false);
  const m = match;
  const cov = m.coverage;

  return (
    <div className="glass-card match-card">
      {/* header row */}
      <div
        className="match-header"
        onClick={() => setOpen((o) => !o)}
        style={{ cursor: "pointer" }}
      >
        <div>
          <h3 style={{ fontSize: "1.05rem", marginBottom: 6 }}>{m.title}</h3>
          <BucketBadge bucket={m.bucket} score={m.score} />
          <div style={{ fontSize: "0.82rem", color: "#888", marginTop: 8 }}>
            Must-haves: {cov.must_met}/{cov.must_total} · Nice-to-haves: {cov.nice_met}/{cov.nice_total}
          </div>
        </div>
        <div style={{ color: "#888", flexShrink: 0 }}>
          {open ? <ChevronUp size={22} /> : <ChevronDown size={22} />}
        </div>
      </div>

      {/* expanded panel */}
      {open && (
        <div className="match-body">
          {/* explanation */}
          <div style={{ marginBottom: 20 }}>
            <h4 style={{ fontSize: "0.9rem", marginBottom: 8, color: "#ccc" }}>Explanation</h4>
            <div style={{ fontSize: "0.88rem", lineHeight: 1.7, color: "#bbb" }}>{m.explanation}</div>
          </div>

          {/* sub-scores */}
          <div style={{ marginBottom: 20 }}>
            <h4 style={{ fontSize: "0.9rem", marginBottom: 12, color: "#ccc" }}>Sub-scores</h4>
            {Object.entries(m.sub_scores).map(([cat, val]) => (
              <SubBar key={cat} label={cat} value={val} />
            ))}
            <SubBar label="coverage" value={cov.covered_score} />
          </div>

          {/* requirements list */}
          <div>
            <h4 style={{ fontSize: "0.9rem", marginBottom: 12, color: "#ccc" }}>
              Requirements ({m.requirement_details.length})
            </h4>
            <div className="req-list">
              {m.requirement_details.map((r: any, i: number) => (
                <ReqRow key={i} r={r} />
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}