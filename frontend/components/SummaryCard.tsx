interface SummaryCardProps {
  title: string;
  summary: string;
}

export default function SummaryCard({ title, summary }: SummaryCardProps) {
  return (
    <div className="card min-h-[260px]">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.32em] text-slate-400">Summary</p>
          <h2 className="mt-2 text-xl font-semibold text-white">{title}</h2>
        </div>
      </div>
      <p className="text-slate-300 leading-7">{summary || "No executive summary available."}</p>
    </div>
  );
}
