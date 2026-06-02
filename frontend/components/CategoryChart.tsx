"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface CategoryData {
  name: string;
  value: number;
}

interface CategoryChartProps {
  data: CategoryData[];
}

export default function CategoryChart({ data }: CategoryChartProps) {
  return (
    <div className="mt-6 h-[320px] w-full rounded-3xl bg-slate-950 p-5">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 24, right: 16, left: -16, bottom: 16 }}>
          <CartesianGrid stroke="#1e293b" vertical={false} />
          <XAxis dataKey="name" tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "#94a3b8", fontSize: 12 }} axisLine={false} tickLine={false} />
          <Tooltip
            cursor={{ fill: "rgba(148, 163, 184, 0.08)" }}
            wrapperStyle={{ borderRadius: 16, backgroundColor: "#0f172a" }}
            contentStyle={{ borderRadius: 16, border: "1px solid #334155" }}
          />
          <Bar dataKey="value" fill="#38bdf8" radius={[12, 12, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
