import React from "react";

export default function Hero({ onGetStarted }: { onGetStarted: () => void }) {
  return (
    <section className="hero container">
      <h1>
        AI-Powered{" "}
        <span className="neon-text">Resume Matcher</span>
      </h1>

      <p>
        Not another keyword matcher. We decompose both the resume and the job
        posting into atomic evidence units, match at the claim level, and give
        you a score that's explainable by construction.
      </p>

      <div className="hero-buttons">
        <button className="btn-primary" onClick={onGetStarted}>
          Get Started
        </button>
      </div>

      <div className="hero-stats">
        <div>
          <strong>Claim-level</strong>
          <br />
          matching
        </div>
        <div>
          <strong>Cited</strong>
          <br />
          explanations
        </div>
        <div>
          <strong>Transparent</strong>
          <br />
          scoring
        </div>
      </div>
    </section>
  );
}