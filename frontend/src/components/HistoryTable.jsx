const BADGES = {
  Safe: 'border-emerald-400/30 bg-emerald-400/15 text-emerald-300',
  Suspicious: 'border-amber-400/30 bg-amber-400/15 text-amber-300',
  Fraud: 'border-rose-400/30 bg-rose-500/15 text-rose-300',
}

// The backend sends times in UTC without a "Z"; add it so the browser shows local time.
function formatTime(value) {
  const iso = value.endsWith('Z') || value.includes('+') ? value : `${value}Z`
  return new Date(iso).toLocaleString('en-IN')
}

export default function HistoryTable({ rows }) {
  return (
    <div className="glass p-6">
      <h2 className="mb-4 text-xl font-bold">
        <span className="gradient-text">Recent transactions</span> 🧾
      </h2>

      {rows.length === 0 ? (
        <p className="text-violet-200/70">Nothing here yet. Go check a transaction!</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-violet-100">
            <thead>
              <tr className="border-b border-white/10 text-violet-300/70">
                <th className="py-2 pr-4">#</th>
                <th className="py-2 pr-4">Time</th>
                <th className="py-2 pr-4">Amount (₹)</th>
                <th className="py-2 pr-4">Hour</th>
                <th className="py-2 pr-4">Distance (km)</th>
                <th className="py-2 pr-4">Fraud %</th>
                <th className="py-2 pr-4">Result</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-b border-white/5 hover:bg-white/5">
                  <td className="py-3 pr-4">{r.id}</td>
                  <td className="py-3 pr-4">{formatTime(r.created_at)}</td>
                  <td className="py-3 pr-4">{r.amount.toLocaleString('en-IN')}</td>
                  <td className="py-3 pr-4">{r.hour}</td>
                  <td className="py-3 pr-4">{r.distance_from_home_km}</td>
                  <td className="py-3 pr-4">{(r.fraud_probability * 100).toFixed(1)}%</td>
                  <td className="py-3 pr-4">
                    <span
                      className={`rounded-full border px-3 py-1 text-xs font-semibold ${BADGES[r.label]}`}
                    >
                      {r.label}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}