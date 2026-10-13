import { useState } from 'react'
import { checkMessage } from '../api'
import ScamResultCard from '../components/ScamResultCard'

// Clickable demo messages
const EXAMPLES = [
  {
    label: 'Fake KYC alert',
    text: 'URGENT: Your SBI account will be blocked today. Update your KYC immediately: https://sbi-kyc-update.xyz/verify',
  },
  {
    label: 'UPI refund trick',
    text: 'Your Paytm refund of Rs 4,999 is pending. Enter your UPI PIN at bit.ly/refund99 to receive the money.',
  },
  {
    label: 'Real bank alert',
    text: 'Rs 1,200 debited from your HDFC account ending 4321 on 12-Oct. If this was not you, call the number on the back of your card.',
  },
]

export default function ScamChecker() {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleCheck() {
    setLoading(true)
    setError('')
    try {
      setResult(await checkMessage(text))
    } catch (err) {
      // A TypeError from fetch usually means the backend isn't running
      if (err instanceof TypeError) {
        setError('Cannot reach the API. Is the backend running on port 8000?')
      } else {
        setError(err.message)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="rounded-2xl border border-rose-400/40 bg-rose-500/10 px-4 py-3 text-rose-200">
          {error}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="glass p-6 lg:col-span-2">
          <h2 className="mb-4 text-xl font-bold">
            <span className="gradient-text">Check a message</span>
          </h2>

          <label className="block text-sm">
            <span className="mb-1 block font-medium text-violet-200">
              Paste the SMS or WhatsApp message
            </span>
            <textarea
              rows={7}
              value={text}
              onChange={(e) => setText(e.target.value)}
              maxLength={2000}
              placeholder="Paste a suspicious message here, including any links..."
              className="field resize-y"
            />
          </label>

          <div className="mt-4">
            <p className="mb-2 text-xs uppercase tracking-wide text-violet-200/60">
              Try an example
            </p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex.label}
                  type="button"
                  onClick={() => setText(ex.text)}
                  className="chip"
                >
                  {ex.label}
                </button>
              ))}
            </div>
          </div>

          <button
            type="button"
            onClick={handleCheck}
            disabled={loading || text.trim().length < 3}
            className="btn-glow mt-6 rounded-2xl px-6 py-3 font-semibold text-white"
          >
            {loading ? 'Checking...' : 'Check message'}
          </button>
        </div>

        <ScamResultCard result={result} />
      </div>
    </div>
  )
}