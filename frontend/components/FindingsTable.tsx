interface Finding {
  title: string;
  severity: string;
  category: string;
  recommendation: string;
}

interface FindingsTableProps {
  findings: Finding[];
}

const severityStyles: Record<string, string> = {
  critical: "bg-red-500/15 text-red-300 border border-red-500/30",
  high: "bg-orange-500/15 text-orange-300 border border-orange-500/30",
  medium: "bg-amber-500/15 text-amber-300 border border-amber-500/30",
  low: "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30",
};

export default function FindingsTable({ findings }: FindingsTableProps) {
  return (
    <div className="space-y-4">
      {findings.map((finding) => (
        <div key={finding.title} className="rounded-3xl border border-slate-800 bg-slate-950/95 p-5">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white">{finding.title}</h3>
              <p className="mt-2 text-sm text-slate-400">{finding.category}</p>
            </div>
            <span className={`badge ${severityStyles[finding.severity.toLowerCase()] || "bg-slate-700 text-slate-100"}`}>
              {finding.severity}
            </span>
          </div>
          <p className="mt-4 text-slate-300">{finding.recommendation}</p>
        </div>
      ))}
    </div>
  );
}
