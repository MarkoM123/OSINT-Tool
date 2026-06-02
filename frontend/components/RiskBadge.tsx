interface RiskBadgeProps {
  level: string;
}

const styles: Record<string, string> = {
  Critical: "bg-red-500/15 text-red-300 border border-red-500/30",
  High: "bg-orange-500/15 text-orange-300 border border-orange-500/30",
  Medium: "bg-amber-500/15 text-amber-300 border border-amber-500/30",
  Low: "bg-emerald-500/15 text-emerald-300 border border-emerald-500/30",
};

export function RiskBadge({ level }: RiskBadgeProps) {
  return (
    <span className={`badge ${styles[level] || "bg-slate-700 text-slate-100"}`}>{level}</span>
  );
}
