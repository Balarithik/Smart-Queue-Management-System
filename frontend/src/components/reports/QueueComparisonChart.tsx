import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export type QueueSummary = {
  queue_id: number
  public_id: string
  name: string
  slug: string
  is_active: boolean
  joins: number
  completed: number
}

type Props = {
  queues: QueueSummary[]
}

export function QueueComparisonChart({ queues }: Props) {
  const chartData = queues.map((q) => ({
    name: q.name.length > 14 ? `${q.name.slice(0, 12)}…` : q.name,
    joins: q.joins,
    completed: q.completed,
  }))

  if (chartData.length === 0) {
    return <p className="text-sm text-slate-500">No queues to compare.</p>
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="#64748b" />
        <YAxis allowDecimals={false} tick={{ fontSize: 11 }} stroke="#64748b" />
        <Tooltip />
        <Legend />
        <Bar dataKey="joins" name="Joins" fill="#4f46e5" radius={[4, 4, 0, 0]} />
        <Bar dataKey="completed" name="Completed" fill="#059669" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
