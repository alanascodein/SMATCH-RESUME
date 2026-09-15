import type { JobInput, MatchResponse, SampleJob } from "./types";

const BASE = "http://127.0.0.1:8000/api";

export async function parseResume(file: File): Promise<{
  filename: string;
  text: string;
  summary: string;
  evidence: any[];
  evidence_count: number;
}> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/parse_resume`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to parse resume.");
  }
  return res.json();
}

export async function matchJobs(
  resumeText: string,
  jobs: JobInput[],
): Promise<MatchResponse> {
  const res = await fetch(`${BASE}/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume_text: resumeText, jobs }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Matching failed.");
  }
  return res.json();
}

export async function getSamples(): Promise<SampleJob[]> {
  const res = await fetch(`${BASE}/samples`);
  return res.json();
}

export async function getSampleJob(id: string): Promise<JobInput> {
  const res = await fetch(`${BASE}/samples/${id}`);
  return res.json();
}

export async function healthCheck(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/health`);
    return res.ok;
  } catch {
    return false;
  }
}