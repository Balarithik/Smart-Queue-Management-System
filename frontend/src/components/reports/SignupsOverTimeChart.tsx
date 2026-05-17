import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export type SignupDay = {
  date: string | null
  count: number
}

type Props = {
  data: SignupDay[]
}

export function SignupsOverTimeChart({ data }: Props) {
  const chartData = data
    .filter((row) => row.date != null)
    .map((row) => ({
      date: row.date as string,
      count: row.count,
    }))

  if (chartData.length === 0) {
    return <p className="text-sm text-slate-500">No signups recorded yet.</p>
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
        <Tooltip />
        <Bar dataKey="count" fill="#4f46e5" name="Signups" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
