import { useEffect, useState } from 'react'
import { getStats, getTransactions, predictTransaction } from '../api'
import TransactionForm from '../components/TransactionForm'
import ResultCard from '../components/ResultCard'
import FraudChart from '../components/FraudChart'
import HistoryTable from '../components/HistoryTable'

export default function Dashboard() {
  const [result, setResult] = useState(null)   // latest prediction
  const [history, setHistory] = useState([])   // recent transactions
  const [stats, setStats] = useState(null)     // counts for the chart
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  function showError(err) {
    // A TypeError from fetch usually means the backend isn't running
    if (err instanceof TypeError) {
      setError('Cannot reach the API. Is the backend running on port 8000?')
    } else {
      setError(err.message)
    }
  }

  // Reload history and stats from the backend
  async function refresh() {
    const [h, s] = await Promise.all([getTransactions(20), getStats()])
    setHistory(h)
    setStats(s)
  }

  // Load data once when the page opens
  useEffect(() => {
    refresh().catch(showError)
  }, [])

  async function handleSubmit(data) {
    setLoading(true)
    setError('')
    try {
      const prediction = await predictTransaction(data)
      setResult(prediction)
      await refresh()
    } catch (err) {
      showError(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="rounded-2xl border border-rose-400/40 bg-rose-500/10 px-4 py-3 text-rose-200">
          😵 {error}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <TransactionForm onSubmit={handleSubmit} loading={loading} />
        </div>
        <ResultCard result={result} />
      </div>

      <FraudChart stats={stats} />
      <HistoryTable rows={history} />
    </div>
  )
}