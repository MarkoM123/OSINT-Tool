"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import ScoreCard from "@/components/ScoreCard";
import CategoryChart from "@/components/CategoryChart";
import SummaryCard from "@/components/SummaryCard";
import FindingsTable from "@/components/FindingsTable";
import { RiskBadge } from "@/components/RiskBadge";

interface TopFinding {
  title: string;
  severity: string;
  category: string;
  recommendation: string;
}

interface AssessmentPayload {
  id: string;
  domain: string;
  status: string;
  score: number;
  category_scores: Record<string, number>;
  executive_summary: string;
  top_findings: TopFinding[];
  created_at: string;
}

const getRiskLevel = (score: number) => {
  if (score <= 40) return "Critical";
  if (score <= 70) return "High";
  if (score <= 85) return "Medium";
  return "Low";
};

export default function DashboardPage() {
  const params = useParams();
  const assessmentId = params?.id as string;
  const [data, setData] = useState<AssessmentPayload | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!assessmentId) {
      setError("Assessment ID is missing.");
      setLoading(false);
      return;
    }

    async function loadAssessment() {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}/assessments/${assessmentId}`);
        if (!response.ok) {
          throw new Error(`Unable to load assessment (${response.status}).`);
        }
        const payload = (await response.json()) as AssessmentPayload;
        setData(payload);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unexpected error.");
      } finally {
        setLoading(false);
      }
    }

    loadAssessment();
  }, [assessmentId]);

  const riskLevel = useMemo(() => (data ? getRiskLevel(data.score) : ""), [data]);

  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-7xl">
        {loading ? (
          <div className="card text-center">
            <p className="text-xl font-medium">Loading assessment dashboard...</p>
          </div>
        ) : error ? (
          <div className="card border border-red-500 bg-slate-900/90 text-red-200">
            <p className="text-xl font-semibold">Unable to load dashboard</p>
            <p className="mt-3 text-slate-300">{error}</p>
          </div>
        ) : data ? (
          <div className="space-y-8">
            <section className="grid gap-6 rounded-3xl border border-slate-800 bg-slate-900/90 p-8 shadow-soft md:grid-cols-[1.4fr_0.6fr]">
              <div>
                <p className="text-sm uppercase tracking-[0.3em] text-slate-400">Assessment</p>
                <h1 className="mt-3 text-4xl font-semibold text-white">{data.domain}</h1>
                <div className="mt-4 flex flex-wrap items-center gap-3 text-slate-300">
                  <span>Assessment date: {new Date(data.created_at).toLocaleDateString()}</span>
                  <span className="h-1 w-1 rounded-full bg-slate-500" />
                  <span>Status: <span className="font-semibold text-white">{data.status}</span></span>
                </div>
              </div>
              <div className="flex flex-col justify-between gap-4">
                <div className="flex items-center justify-between rounded-3xl bg-slate-950/90 p-5">
                  <div>
                    <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Overall Exposure Score</p>
                    <p className="mt-2 text-5xl font-semibold text-white">{data.score}</p>
                  </div>
                  <RiskBadge level={riskLevel} />
                </div>
                <div className="rounded-3xl bg-slate-950/90 p-5">
                  <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Risk indicator</p>
                  <p className="mt-3 text-3xl font-semibold text-white">{riskLevel}</p>
                </div>
              </div>
            </section>

            <section className="grid gap-6 xl:grid-cols-[0.65fr_0.35fr]">
              <div className="card">
                <h2 className="text-xl font-semibold text-white">Category Breakdown</h2>
                <p className="mt-2 text-sm text-slate-400">Exposure scores by security category.</p>
                <CategoryChart data={Object.entries(data.category_scores).map(([key, value]) => ({ name: key.replace(/_/g, " "), value }))} />
              </div>

              <SummaryCard title="Executive Summary" summary={data.executive_summary} />
            </section>

            <section className="grid gap-6 lg:grid-cols-[0.6fr_0.4fr]">
              <div className="card">
                <div className="mb-6 flex items-center justify-between">
                  <div>
                    <p className="text-sm uppercase tracking-[0.24em] text-slate-400">Top Findings</p>
                    <h2 className="text-xl font-semibold text-white">Priority issues</h2>
                  </div>
                </div>
                <FindingsTable findings={data.top_findings} />
              </div>
              <div className="card">
                <ScoreCard score={data.score} />
              </div>
            </section>
          </div>
        ) : null}
      </div>
    </main>
  );
}
