export interface ResumeEvidence {
  text: string;
  skills: string[];
  soft: string[];
  domain: string[];
  years: number;
  quantified: boolean;
}

export interface ResumeAnalysis {
  filename: string;
  text: string;
  summary: string;
  evidence: ResumeEvidence[];
  evidence_count: number;
}

export interface RequirementDetail {
  text: string;
  label: string;
  score: number;
  must_have: boolean;
  skills: string[];
  evidence_text: string | null;
  reason: string | null;
  status: "matched" | "partial" | "missing";
  reworded: boolean;
}

export interface JobRequirement {
  text: string;
  must_have: boolean;
  category: string;
  skills: string[];
  soft: string[];
  domain: string[];
  years: number;
}

export interface JobParse {
  title: string;
  requirements: JobRequirement[];
}

export interface MatchResult {
  id: string;
  title: string;
  score: number;
  bucket: "Excellent" | "Strong" | "Potential" | "Low";
  sub_scores: Record<string, number>;
  coverage: {
    must_met: number;
    must_total: number;
    nice_met: number;
    nice_total: number;
    covered_score: number;
  };
  requirement_details: RequirementDetail[];
  explanation: string;
}

export interface MatchResponse {
  resume_name: string;
  evidence_count: number;
  matches: MatchResult[];
}

export interface JobInput {
  id: string;
  title: string;
  text: string;
}

export interface SampleJob {
  id: string;
  title: string;
}