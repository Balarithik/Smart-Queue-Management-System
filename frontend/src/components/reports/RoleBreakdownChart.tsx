import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts'

type Props = {
  user: number
  organization: number
  admin: number
}

const COLORS = ['#6366f1', '#0ea5e9', '#64748b']

export function RoleBreakdownChart({ user, organization, admin }: Props) {
  const data = [
    { name: 'User', value: user },
    { name: 'Organization', value: organization },
    { name: 'Admin', value: admin },
  ].filter((row) => row.value > 0)

  if (data.length === 0) {
    return <p className="text-sm text-slate-500">No users yet.</p>
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
