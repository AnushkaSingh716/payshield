// Colors for each label. (Full class names are written out so Tailwind can find them.)
const STYLES = {
  Safe: { box: 'border-green-400 bg-green-50', text: 'text-green-700', icon: '✅' },
  Suspicious: { box: 'border-amber-400 bg-amber-50', text: 'text-amber-700', icon: '⚠️' },
  Fraud: { box: 'border-red-400 bg-red-50', text: 'text-red-700', icon: '🚨' },
}

export default function ResultCard({ result }) {
  if (!result) {
    return (
      <div className="flex items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-white p-6 text-center text-slate-500">
        Submit a transaction to see the result here.
      </div>
    )
  }

  const style = STYLES[result.label] || STYLES.Suspicious
  const percent = (result.fraud_probability * 100).toFixed(1)

  return (
    <div className={`rounded-xl border-2 p-6 ${style.box}`}>
      <p className="text-sm font-medium text-slate-600">Result</p>
      <p className={`mt-1 text-3xl font-bold ${style.text}`}>
        {style.icon} {result.label}
      </p>
      <p className="mt-3 text-slate-700">
        Fraud probability: <span className="font-semibold">{percent}%</span>
      </p>

      {/* Simple progress bar for the probability */}
      <div className="mt-2 h-3 w-full overflow-hidden rounded-full bg-white">
        <div
          className="h-full bg-slate-700"
          style={{ width: `${Math.min(100, result.fraud_probability * 100)}%` }}
        />
      </div>

      <p className="mt-4 text-sm text-slate-600">
        ₹{result.amount.toLocaleString('en-IN')} at {result.hour}:00, transaction #{result.id}
      </p>
    </div>
  )
}