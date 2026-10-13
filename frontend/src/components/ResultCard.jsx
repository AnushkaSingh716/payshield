// Colors for each label. (Full class names are written out so Tailwind can find them.)
const STYLES = {
  Safe: {
    box: 'border-emerald-400/50 bg-emerald-400/10 shadow-[0_0_40px_rgba(52,211,153,0.25)]',
    text: 'text-emerald-300',
    bar: 'from-emerald-400 to-cyan-400',
    dot: 'bg-emerald-400 shadow-[0_0_14px_rgba(52,211,153,0.9)]',
    note: 'Looks legit. Vibes immaculate.',
  },
  Suspicious: {
    box: 'border-amber-400/50 bg-amber-400/10 shadow-[0_0_40px_rgba(251,191,36,0.25)]',
    text: 'text-amber-300',
    bar: 'from-amber-400 to-orange-400',
    dot: 'bg-amber-400 shadow-[0_0_14px_rgba(251,191,36,0.9)]',
    note: 'Something feels off. Double-check this one.',
  },
  Fraud: {
    box: 'border-rose-400/50 bg-rose-500/10 shadow-[0_0_40px_rgba(251,113,133,0.3)]',
    text: 'text-rose-300',
    bar: 'from-rose-500 to-pink-500',
    dot: 'bg-rose-400 shadow-[0_0_14px_rgba(251,113,133,0.9)]',
    note: 'Major red flags. Block it and verify.',
  },
}

export default function ResultCard({ result }) {
  if (!result) {
    return (
      <div className="glass flex flex-col items-center justify-center p-6 text-center text-violet-200/80">
        <div className="h-4 w-4 animate-pulse rounded-full bg-violet-400 shadow-[0_0_16px_rgba(167,139,250,0.9)]" />
        <p className="mt-4">Waiting for a transaction...</p>
        <p className="text-sm text-violet-200/50">Your result shows up here.</p>
      </div>
    )
  }

  const style = STYLES[result.label] || STYLES.Suspicious
  const percent = (result.fraud_probability * 100).toFixed(1)

  return (
    // key={result.id} replays the pop-in animation for every new result
    <div
      key={result.id}
      className={`pop-in rounded-3xl border p-6 backdrop-blur ${style.box}`}
    >
      <p className="text-sm font-medium text-violet-200/70">Result</p>
      <p className={`mt-1 flex items-center gap-3 text-4xl font-bold ${style.text}`}>
        <span className={`h-4 w-4 rounded-full ${style.dot}`} />
        {result.label}
      </p>
      <p className="mt-1 text-sm text-violet-100/80">{style.note}</p>

      <p className="mt-4 text-violet-100">
        Fraud probability: <span className="text-xl font-bold">{percent}%</span>
      </p>

      {/* Probability bar */}
      <div className="mt-2 h-3 w-full overflow-hidden rounded-full bg-white/10">
        <div
          className={`h-full rounded-full bg-gradient-to-r transition-all duration-700 ${style.bar}`}
          style={{ width: `${Math.min(100, result.fraud_probability * 100)}%` }}
        />
      </div>

      <p className="mt-4 text-sm text-violet-200/70">
        ₹{result.amount.toLocaleString('en-IN')} at {result.hour}:00 · transaction #{result.id}
      </p>
    </div>
  )
}