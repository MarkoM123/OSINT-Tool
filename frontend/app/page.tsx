import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-950 px-6 py-10 text-slate-100">
      <div className="mx-auto max-w-5xl">
        <div className="card border-slate-800/90">
          <h1 className="text-4xl font-semibold text-white">Exposure Intelligence Platform</h1>
          <p className="mt-4 max-w-2xl text-slate-300">
            Production-ready cybersecurity dashboard for executive exposure reporting.
            Use the assessment landing page to view assessment details and risk insights.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link
              href="/dashboard/example-id"
              className="rounded-2xl bg-slate-800 px-5 py-3 text-white transition hover:bg-slate-700"
            >
              View sample dashboard
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
