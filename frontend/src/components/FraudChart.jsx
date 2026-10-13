import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

export default function FraudChart({ stats }) {
  if (!stats) {
    return <div className="rounded-xl bg-white p-6 shadow">Loading stats...</div>
  }

  const data = [
    { name: 'Safe', count: stats.safe, color: '#16a34a' },
    { name: 'Suspicious', count: stats.suspicious, color: '#d97706' },
    { name: 'Fraud', count: stats.fraud, color: '#dc2626' },
  ]

  return (
    <div className="rounded-xl bg-white p-6 shadow">
      <h2 className="mb-4 text-lg font-semibold">Fraud vs legit transactions</h2>

      <div className="mb-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatBox label="Total checked" value={stats.total} />
        <StatBox label="Safe" value={stats.safe} />
        <StatBox label="Fraud" value={stats.fraud} />
        <StatBox label="Fraud rate" value={`${stats.fraud_rate}%`} />
      </div>

      {stats.total === 0 ? (
        <p className="text-slate-500">No data yet. Check a transaction to fill the chart.</p>
      ) : (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count">
                {data.map((d) => (
                  <Cell key={d.name} fill={d.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}

function StatBox({ label, value }) {
  return (
    <div className="rounded-lg bg-slate-50 p-3">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="text-xl font-bold">{value}</p>
    </div>
  )
}