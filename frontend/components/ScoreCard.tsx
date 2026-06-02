interface ScoreCardProps {
  score: number;
}

const getColor = (score: number) => {
  if (score <= 40) return "from-red-500 to-rose-600";
  if (score <= 70) return "from-orange-500 to-amber-600";
  return "from-emerald-500 to-lime-500";
};

export default function ScoreCard({ score }: ScoreCardProps) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-gradient-to-br p-6 shadow-soft">
      <p className="text-sm uppercase tracking-[0.32em] text-slate-400">Exposure Score</p>
      <div className={`mt-6 flex items-end gap-4 rounded-3xl bg-slate-950 p-6 text-white shadow-lg ${getColor(score)}`}>
        <span className="text-6xl font-semibold">{score}</span>
        <span className="text-sm text-slate-200">/100</span>
      </div>
      <p className="mt-5 text-sm text-slate-400">Higher scores reflect stronger exposure posture.</p>
    </div>
  );
}
