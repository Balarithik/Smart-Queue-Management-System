import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

type Props = {
  waiting: number
  called: number
  completed: number
}

const COLORS = ['#f59e0b', '#4f46e5', '#059669']

export function StatusBreakdownChart({ waiting, called, completed }: Props) {
  const data = [
    { name: 'Waiting', value: waiting },
    { name: 'Called', value: called },
    { name: 'Completed', value: completed },
  ].filter((row) => row.value > 0)

  if (data.length === 0) {
    return <p className="text-sm text-slate-500">No entries yet.</p>
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={90}
          label={({ name, value }) => `${name}: ${value}`}
        >
          {data.map((_, index) => (
            <Cell key={index} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}
