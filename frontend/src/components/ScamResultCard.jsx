import FeedbackButtons from './FeedbackButtons'

// Colors for each label. (Full class names are written out so Tailwind can find them.)
const STYLES = {
  Safe: {
    box: 'border-emerald-400/50 bg-emerald-400/10 shadow-[0_0_40px_rgba(52,211,153,0.25)]',
    text: 'text-emerald-300',
    bar: 'from-emerald-400 to-cyan-400',
    dot: 'bg-emerald-400 shadow-[0_0_14px_rgba(52,211,153,0.9)]',
    note: 'No scam signals found.',
  },
  Suspicious: {
    box: 'border-amber-400/50 bg-amber-400/10 shadow-[0_0_40px_rgba(251,191,36,0.25)]',
    text: 'text-amber-300',
    bar: 'from-amber-400 to-orange-400',
    dot: 'bg-amber-400 shadow-[0_0_14px_rgba(251,191,36,0.9)]',
    note: 'Be careful. Do not click links or share details.',
  },
  Scam: {
    box: 'border-rose-400/50 bg-rose-500/10 shadow-[0_0_40px_rgba(251,113,133,0.3)]',
    text: 'text-rose-300',
    bar: 'from-rose-500 to-pink-500',
    dot: 'bg-rose-400 shadow-[0_0_14px_rgba(251,113,133,0.9)]',
    note: 'This looks like a scam. Do not reply, click or pay.',
  },
}

export default function ScamResultCard({ result }) {
  if (!result) {
    return (
      <div className="glass flex flex-col items-center justify-center p-6 text-center text-violet-200/80">
        <div className="h-4 w-4 animate-pulse rounded-full bg-violet-400 shadow-[0_0_16px_rgba(167,139,250,0.9)]" />
        <p className="mt-4">Waiting for a message...</p>
        <p className="text-sm text-violet-200/50">Your result shows up here.</p>
      </div>
    )
  }

  const style = STYLES[result.label] || STYLES.Suspicious

  return (
    // key={result.id} replays the pop-in animation for every new result
    <div
      key={result.id}
      className={`pop-in rounded-3xl border p-6 backdrop-blur ${style.box}`}
    >
      <p className="text-sm font-medium text-violet-200/70">Risk level</p>
      <p className={`mt-1 flex items-center gap-3 text-4xl font-bold ${style.text}`}>
        <span className={`h-4 w-4 rounded-full ${style.dot}`} />
        {result.label}
      </p>
      <p className="mt-1 text-sm text-violet-100/80">{style.note}</p>

      <p className="mt-4 text-violet-100">
        Risk score: <span className="text-xl font-bold">{result.risk_score}%</span>
      </p>
      <div className="mt-2 h-3 w-full overflow-hidden rounded-full bg-white/10">
        <div
          className={`h-full rounded-full bg-gradient-to-r transition-all duration-700 ${style.bar}`}
          style={{ width: `${Math.min(100, result.risk_score)}%` }}
        />
      </div>

      {/* Where the score came from */}
      <div className="mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
          <p className="text-xs text-violet-200/70">Message wording</p>
          <p className="text-lg font-bold">{result.text_score}%</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-3">
          <p className="text-xs text-violet-200/70">Link risk</p>
          <p className="text-lg font-bold">{result.link_score}%</p>
        </div>
      </div>

      {/* Plain-English reasons */}
      {result.reasons.length > 0 && (
        <div className="mt-5">
          <p className="mb-2 text-xs uppercase tracking-wide text-violet-200/60">
            Why this result
          </p>
          <ul className="space-y-2">
            {result.reasons.map((r, i) => (
              <li key={i} className="flex items-start gap-3 text-sm text-violet-50">
                <span
                  className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${
                    r.direction === 'increases' ? 'bg-rose-400' : 'bg-emerald-400'
                  }`}
                />
                <span>{r.text}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Links found in the message */}
      {result.urls_found.length > 0 && (
        <div className="mt-5">
          <p className="mb-2 text-xs uppercase tracking-wide text-violet-200/60">
            Links found
          </p>
          <ul className="space-y-2">
            {result.urls_found.map((url) => (
              <li
                key={url}
                className="break-all rounded-lg bg-black/30 px-3 py-2 font-mono text-xs text-violet-100"
              >
                {url}
              </li>
            ))}
          </ul>
        </div>
      )}

      <FeedbackButtons kind="message" targetId={result.id} />
    </div>
  )
}