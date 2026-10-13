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
    return <div className="glass p-6 text-violet-200">Loading stats...</div>
  }

  const data = [
    { name: 'Safe', count: stats.safe, color: '#34d399' },
    { name: 'Suspicious', count: stats.suspicious, color: '#fbbf24' },
    { name: 'Fraud', count: stats.fraud, color: '#fb7185' },
  ]

  return (
    <div className="glass p-6">
      <h2 className="mb-4 text-xl font-bold">
        <span className="gradient-text">Fraud vs legit</span> 📈
      </h2>

      <div className="mb-5 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <StatBox emoji="📊" label="Total checked" value={stats.total} />
        <StatBox emoji="😎" label="Safe" value={stats.safe} />
        <StatBox emoji="🚨" label="Fraud" value={stats.fraud} />
        <StatBox emoji="🎯" label="Fraud rate" value={`${stats.fraud_rate}%`} />
      </div>

      {stats.total === 0 ? (
        <p className="text-violet-200/70">
          No data yet. Check a transaction to light up the chart.
        </p>
      ) : (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="name" tick={{ fill: '#c4b5fd' }} stroke="rgba(255,255,255,0.2)" />
              <YAxis
                allowDecimals={false}
                tick={{ fill: '#c4b5fd' }}
                stroke="rgba(255,255,255,0.2)"
              />
              <Tooltip
                cursor={{ fill: 'rgba(255,255,255,0.06)' }}
                contentStyle={{
                  background: '#1e1b4b',
                  border: '1px solid rgba(255,255,255,0.15)',
                  borderRadius: 12,
                  color: '#fff',
                }}
                labelStyle={{ color: '#fff' }}
                itemStyle={{ color: '#fff' }}
              />
              <Bar dataKey="count" radius={[10, 10, 0, 0]}>
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

function StatBox({ emoji, label, value }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="text-xs text-violet-200/70">
        {emoji} {label}
      </p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
    </div>
  )
}