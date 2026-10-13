const BADGES = {
  Safe: 'bg-green-100 text-green-700',
  Suspicious: 'bg-amber-100 text-amber-700',
  Fraud: 'bg-red-100 text-red-700',
}

// The backend sends times in UTC without a "Z"; add it so the browser shows local time.
function formatTime(value) {
  const iso = value.endsWith('Z') || value.includes('+') ? value : `${value}Z`
  return new Date(iso).toLocaleString('en-IN')
}

export default function HistoryTable({ rows }) {
  return (
    <div className="rounded-xl bg-white p-6 shadow">
      <h2 className="mb-4 text-lg font-semibold">Recent transactions</h2>

      {rows.length === 0 ? (
        <p className="text-slate-500">No transactions yet.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500">
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
                <tr key={r.id} className="border-b border-slate-100">
                  <td className="py-2 pr-4">{r.id}</td>
                  <td className="py-2 pr-4">{formatTime(r.created_at)}</td>
                  <td className="py-2 pr-4">{r.amount.toLocaleString('en-IN')}</td>
                  <td className="py-2 pr-4">{r.hour}</td>
                  <td className="py-2 pr-4">{r.distance_from_home_km}</td>
                  <td className="py-2 pr-4">{(r.fraud_probability * 100).toFixed(1)}%</td>
                  <td className="py-2 pr-4">
                    <span
                      className={`rounded-full px-2 py-1 text-xs font-medium ${BADGES[r.label]}`}
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