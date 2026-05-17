import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export type DailySeriesPoint = {
  date: string
  joins: number
  called?: number
  completed: number
}

type Props = {
  data: DailySeriesPoint[]
}

function formatDate(iso: string) {
  const d = new Date(iso + 'T12:00:00')
  return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

export function EntriesOverTimeChart({ data }: Props) {
  const chartData = data.map((row) => ({
    ...row,
    label: formatDate(row.date),
  }))

  if (chartData.length === 0) {
    return <p className="text-sm text-slate-500">No activity in this period.</p>
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <AreaChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="label" tick={{ fontSize: 11 }} stroke="#64748b" />
        <YAxis allowDecimals={false} tick={{ fontSize: 11 }} stroke="#64748b" />
        <Tooltip />
        <Legend />
        <Area
          type="monotone"
          dataKey="joins"
          name="Joins"
          stroke="#4f46e5"
          fill="#818cf8"
          fillOpacity={0.35}
        />
        <Area
          type="monotone"
          dataKey="completed"
          name="Completed"
          stroke="#059669"
          fill="#34d399"
          fillOpacity={0.35}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}
