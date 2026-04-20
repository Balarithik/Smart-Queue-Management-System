import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../../app/api";

export function AnalyticsPage() {
  const [rows, setRows] = useState<any[]>([]);

  useEffect(() => {
    api.get("/analytics/").then((res) => setRows(res.data.results ?? res.data));
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-xl font-semibold mb-4">Analytics</h2>
      <div className="card h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period_start" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="throughput" fill="#2563eb" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
