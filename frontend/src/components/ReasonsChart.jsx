import {
  Bar,
  BarChart,
  Cell,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

// Small horizontal bar chart: red pushes toward fraud, green toward safe.
export default function ReasonsChart({ contributions }) {
  if (!contributions || contributions.length === 0) return null

  const data = contributions.map((c) => ({ name: c.feature, impact: c.impact }))

  return (
    <div className="mt-5">
      <p className="mb-2 text-xs uppercase tracking-wide text-violet-200/60">
        What pushed the score
      </p>

      <div style={{ height: 40 + data.length * 28 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 0, right: 10, bottom: 0, left: 0 }}
          >
            <XAxis type="number" hide />
            <YAxis
              type="category"
              dataKey="name"
              width={120}
              tick={{ fill: '#ddd6fe', fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />
            <ReferenceLine x={0} stroke="rgba(255,255,255,0.3)" />
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
              formatter={(value) => [
                value > 0 ? `+${value} toward fraud` : `${value} toward safe`,
                'Impact',
              ]}
            />
            <Bar dataKey="impact" radius={4}>
              {data.map((d) => (
                <Cell key={d.name} fill={d.impact > 0 ? '#fb7185' : '#34d399'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <p className="mt-1 text-xs text-violet-200/50">
        Red pushes toward fraud, green toward safe.
      </p>
    </div>
  )
}