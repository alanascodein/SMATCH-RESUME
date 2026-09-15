import React, { useState, useEffect, useRef } from "react";
import Hero from "./components/Hero";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import MatchCard from "./components/MatchCard";
import type { JobInput, MatchResult, MatchResponse, SampleJob } from "./types";
import { parseResume, matchJobs, getSamples, getSampleJob, healthCheck } from "./api";
import { Upload, FileText, Plus, Trash2, Loader2, Zap, AlertCircle } from "lucide-react";

let jobCounter = 0;

export default function App() {
  // ---- state ----
  const [serverOk, setServerOk] = useState(true);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState("");
  const [resumeLabel, setResumeLabel] = useState("");
  const [parsingResume, setParsingResume] = useState(false);

  const [jobs, setJobs] = useState<JobInput[]>([]);
  const [jobText, setJobText] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [samples, setSamples] = useState<SampleJob[]>([]);

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<MatchResponse | null>(null);
  const [error, setError] = useState("");

  const inputRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    healthCheck().then(setServerOk);
    getSamples().then(setSamples).catch(() => {});
  }, []);

  // ---- resume upload ----
  async function handleResumeUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setResumeFile(file);
    setResumeLabel(file.name);
    setParsingResume(true);
    setError("");
    try {
      const data = await parseResume(file);
      setResumeText(data.text);
      setResumeLabel(data.filename + ` (${data.evidence_count} evidence units)`);
    } catch (err: any) {
      setError(err.message);
    }
    setParsingResume(false);
  }

  function handleClearResume() {
    setResumeFile(null);
    setResumeText("");
    setResumeLabel("");
  }

  // ---- jobs ----
  async function addJob() {
    if (!jobText.trim()) return;
    const id = `job_${++jobCounter}`;
    const title = jobTitle.trim() || `Job ${jobCounter}`;
    setJobs((j) => [...j, { id, title, text: jobText.trim() }]);
    setJobText("");
    setJobTitle("");
  }

  async function addSample(id: string) {
    try {
      const data = await getSampleJob(id);
      const uid = `job_${++jobCounter}`;
      setJobs((j) => [...j, { id: uid, title: data.title, text: data.text }]);
    } catch {}
  }

  function removeJob(idx: number) {
    setJobs((j) => j.filter((_, i) => i !== idx));
  }

  // ---- match ----
  async function runMatch() {
    if (!resumeText.trim()) {
      setError("Please upload or paste a resume first.");
      return;
    }
    if (jobs.length === 0) {
      setError("Add at least one job posting to match against.");
      return;
    }
    setLoading(true);
    setError("");
    setResults(null);
    try {
      const res = await matchJobs(resumeText, jobs);
      setResults(res);
    } catch (err: any) {
      setError(err.message);
    }
    setLoading(false);
  }

  function scrollToInput() {
    inputRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  return (
    <div className="app-container">
      <div className="blob" style={{ top: -200, left: -200 }} />
      <div className="blob" style={{ bottom: -200, right: -200, opacity: 0.2 }} />
      <Navbar />

      <main className="main-content">
        <Hero onGetStarted={scrollToInput} />

        {/* Server status */}
        {!serverOk && (
          <div className="container" style={{ marginBottom: 20 }}>
            <div className="glass-card" style={{ padding: 14, display: "flex", alignItems: "center", gap: 10, borderColor: "#f43f5e44" }}>
              <AlertCircle size={18} color="#f43f5e" />
              <span style={{ fontSize: "0.85rem", color: "#f43f5e" }}>
                Backend not running. Start with: <code>cd backend && python main.py</code>
              </span>
            </div>
          </div>
        )}

        {/* ====== INPUT SECTION ====== */}
        <div className="container" ref={inputRef} id="input-section">
          <div className="section-header" style={{ marginBottom: 32 }}>
            <h2>
              Upload & <span className="neon-text">Match</span>
            </h2>
          </div>

          <div className="input-grid">
            {/* LEFT — Resume */}
            <div className="glass-card input-card">
              <h3 style={{ marginBottom: 16, fontSize: "0.95rem" }}>Resume</h3>

              <label className="upload-zone">
                <input
                  type="file"
                  accept=".pdf,.docx,.txt,.doc"
                  onChange={handleResumeUpload}
                  style={{ display: "none" }}
                />
                {parsingResume ? (
                  <Loader2 size={22} className="spin-icon" />
                ) : (
                  <Upload size={22} color="#a3e635" />
                )}
                <span style={{ fontSize: "0.85rem", color: "#999" }}>
                  {parsingResume ? "Parsing…" : "Click to upload PDF / DOCX / TXT"}
                </span>
              </label>

              {resumeLabel && (
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 12 }}>
                  <FileText size={16} color="#a3e635" />
                  <span style={{ fontSize: "0.82rem", flex: 1, color: "#ccc" }}>{resumeLabel}</span>
                  <button
                    onClick={handleClearResume}
                    style={{ background: "none", border: "none", cursor: "pointer", color: "#888" }}
                    title="Clear"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              )}

              <textarea
                className="paste-textarea"
                placeholder="Or paste resume text here…"
                value={resumeText}
                onChange={(e) => { setResumeText(e.target.value); setResumeLabel("Pasted text"); }}
                rows={10}
              />
            </div>

            {/* RIGHT — Jobs */}
            <div className="glass-card input-card">
              <h3 style={{ marginBottom: 16, fontSize: "0.95rem" }}>Job Postings ({jobs.length})</h3>

              {/* sample chips */}
              {samples.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: "0.78rem", color: "#888", marginBottom: 8 }}>Load a sample posting:</div>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    {samples.map((s) => (
                      <button key={s.id} className="sample-chip" onClick={() => addSample(s.id)}>
                        {s.title}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <input
                className="job-input"
                placeholder="Job title (optional)"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
              />
              <textarea
                className="paste-textarea"
                placeholder="Paste job posting text here…"
                value={jobText}
                onChange={(e) => setJobText(e.target.value)}
                rows={5}
              />
              <button
                className="btn-primary"
                style={{ width: "100%", justifyContent: "center", marginTop: 12, padding: "12px 20px", fontSize: "0.9rem" }}
                onClick={addJob}
                disabled={!jobText.trim()}
              >
                <Plus size={18} /> Add Job Posting
              </button>

              {/* added jobs list */}
              {jobs.length > 0 && (
                <div className="jobs-list">
                  {jobs.map((j, i) => (
                    <div key={j.id} className="job-item">
                      <span style={{ flex: 1, fontSize: "0.85rem" }}>{j.title}</span>
                      <button onClick={() => removeJob(i)} className="job-remove-btn" title="Remove">
                        <Trash2 size={14} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Analyze button */}
          <div style={{ textAlign: "center", marginTop: 32 }}>
            <button
              className="btn-primary analyze-btn"
              onClick={runMatch}
              disabled={loading || !resumeText.trim() || jobs.length === 0}
            >
              {loading ? <Loader2 size={20} className="spin-icon" /> : <Zap size={20} />}
              {loading ? "Analyzing…" : "Analyze & Rank"}
            </button>
          </div>

          {error && (
            <div className="glass-card" style={{ padding: 14, marginTop: 16, borderColor: "#f43f5e44", textAlign: "center" }}>
              <span style={{ fontSize: "0.85rem", color: "#f43f5e" }}>{error}</span>
            </div>
          )}
        </div>

        {/* ====== RESULTS ====== */}
        {results && (
          <div className="container results-section" id="results">
            <div className="section-header" style={{ marginBottom: 24 }}>
              <h2>
                Results — <span className="neon-text">{results.matches.length}</span> job
                {results.matches.length !== 1 ? "s" : ""} matched
              </h2>
              <p>Resume: {results.resume_name} · {results.evidence_count} evidence units detected</p>
            </div>

            <div className="results-list">
              {results.matches.map((m) => (
                <MatchCard key={m.id} match={m} />
              ))}
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}