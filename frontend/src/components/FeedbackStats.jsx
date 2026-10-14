import { useEffect, useState } from 'react'
import { getFeedbackStats } from '../api'

function Box({ label, value }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="text-xs text-violet-200/70">{label}</p>
      <p className="mt-1 text-2xl font-bold">{value}</p>
    </div>
  )
}

export default function FeedbackStats() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    function load() {
      getFeedbackStats()
        .then(setStats)
        .catch(() => {}) // if the API is down, the main pages already show an error
    }
    load()
    // FeedbackButtons fires this event after every report
    window.addEventListener('feedback-sent', load)
    return () => window.removeEventListener('feedback-sent', load)
  }, [])

  if (!stats) return null

  return (
    <div className="glass p-6">
      <h2 className="mb-4 text-xl font-bold">
        <span className="gradient-text">Feedback stats</span>
      </h2>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        <Box label="Reports received" value={stats.total} />
        <Box label="Marked as fraud" value={stats.fraud_reports} />
        <Box label="Marked as mine" value={stats.this_was_me} />
        <Box label="Wrong scam results" value={stats.wrong_result_reports} />
        <Box label="Fraud model" value={stats.fraud_model_version} />
        <Box label="Scam model" value={stats.scam_model_version} />
      </div>
      <p className="mt-3 text-xs text-violet-200/50">
        Reports are used the next time the models are retrained.
      </p>
    </div>
  )
}