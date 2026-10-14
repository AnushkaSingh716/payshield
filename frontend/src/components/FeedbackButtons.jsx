import { useState } from 'react'
import { sendFeedback } from '../api'

const OPTIONS = {
  transaction: {
    title: 'Give feedback',
    buttons: [
      { action: 'report_fraud', label: 'Report as fraud', done: 'Thanks. Marked as fraud.' },
      { action: 'this_was_me', label: 'This was me', done: 'Thanks. Marked as a genuine transaction.' },
    ],
  },
  message: {
    title: 'Think we got it wrong?',
    buttons: [
      { action: 'report_wrong', label: 'Report wrong result', done: 'Thanks. Your correction was saved.' },
    ],
  },
}

// kind: "transaction" or "message", targetId: the prediction or scam check id
export default function FeedbackButtons({ kind, targetId }) {
  const [busy, setBusy] = useState(false)
  const [doneText, setDoneText] = useState('')
  const [error, setError] = useState('')
  const config = OPTIONS[kind]

  async function handleClick(option) {
    setBusy(true)
    setError('')
    try {
      await sendFeedback({ kind, target_id: targetId, action: option.action })
      setDoneText(option.done)
      // Tell the Feedback stats panel to refresh itself
      window.dispatchEvent(new Event('feedback-sent'))
    } catch (err) {
      setError(err instanceof TypeError ? 'Cannot reach the API.' : err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mt-5 border-t border-white/10 pt-4">
      <p className="mb-2 text-xs uppercase tracking-wide text-violet-200/60">
        {config.title}
      </p>
      <div className="flex flex-wrap gap-2">
        {config.buttons.map((option) => (
          <button
            key={option.action}
            type="button"
            disabled={busy}
            onClick={() => handleClick(option)}
            className="chip disabled:opacity-50"
          >
            {option.label}
          </button>
        ))}
      </div>
      {doneText && <p className="mt-2 text-sm text-emerald-300">{doneText}</p>}
      {error && <p className="mt-2 text-sm text-rose-300">{error}</p>}
    </div>
  )
}
