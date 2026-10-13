import { useState } from 'react'

// The number fields on the form. "name" must match what the backend expects.
const NUMBER_FIELDS = [
  { name: 'amount', label: 'Amount (₹)', min: 0.01, step: 0.01 },
  { name: 'avg_amount_30d', label: 'Usual average spend (₹)', min: 0.01, step: 0.01 },
  { name: 'hour', label: 'Hour of day (0-23)', min: 0, max: 23, step: 1 },
  { name: 'distance_from_home_km', label: 'Distance from home (km)', min: 0, step: 0.1 },
  { name: 'txn_count_24h', label: 'Transactions in last 24h', min: 0, step: 1 },
  { name: 'account_age_days', label: 'Account age (days)', min: 0, step: 1 },
]

const EMPTY = {
  amount: '',
  avg_amount_30d: '',
  hour: '',
  distance_from_home_km: '',
  txn_count_24h: '',
  account_age_days: '',
  is_new_device: false,
  is_international: false,
}

// One-click examples, handy for demos
const EXAMPLES = {
  normal: {
    amount: '1200',
    avg_amount_30d: '1500',
    hour: '14',
    distance_from_home_km: '5',
    txn_count_24h: '2',
    account_age_days: '800',
    is_new_device: false,
    is_international: false,
  },
  risky: {
    amount: '90000',
    avg_amount_30d: '1500',
    hour: '3',
    distance_from_home_km: '400',
    txn_count_24h: '9',
    account_age_days: '20',
    is_new_device: true,
    is_international: true,
  },
}

export default function TransactionForm({ onSubmit, loading }) {
  const [form, setForm] = useState(EMPTY)

  function handleChange(e) {
    const { name, value, type, checked } = e.target
    setForm({ ...form, [name]: type === 'checkbox' ? checked : value })
  }

  function handleSubmit(e) {
    e.preventDefault()
    // Turn the text boxes into real numbers before sending
    const payload = {
      is_new_device: form.is_new_device,
      is_international: form.is_international,
    }
    NUMBER_FIELDS.forEach((f) => {
      payload[f.name] = Number(form[f.name])
    })
    onSubmit(payload)
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-xl bg-white p-6 shadow">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold">Check a transaction</h2>
        <div className="flex gap-2 text-sm">
          <button
            type="button"
            onClick={() => setForm(EXAMPLES.normal)}
            className="rounded border border-slate-300 px-3 py-1 hover:bg-slate-50"
          >
            Fill normal example
          </button>
          <button
            type="button"
            onClick={() => setForm(EXAMPLES.risky)}
            className="rounded border border-slate-300 px-3 py-1 hover:bg-slate-50"
          >
            Fill risky example
          </button>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {NUMBER_FIELDS.map((f) => (
          <label key={f.name} className="block text-sm">
            <span className="mb-1 block font-medium">{f.label}</span>
            <input
              type="number"
              name={f.name}
              value={form[f.name]}
              onChange={handleChange}
              min={f.min}
              max={f.max}
              step={f.step}
              required
              className="w-full rounded border border-slate-300 px-3 py-2 focus:border-slate-500 focus:outline-none"
            />
          </label>
        ))}
      </div>

      <div className="mt-4 flex flex-wrap gap-6 text-sm">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            name="is_new_device"
            checked={form.is_new_device}
            onChange={handleChange}
          />
          New device
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            name="is_international"
            checked={form.is_international}
            onChange={handleChange}
          />
          International transaction
        </label>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="mt-6 rounded-lg bg-slate-900 px-5 py-2 font-medium text-white hover:bg-slate-700 disabled:opacity-50"
      >
        {loading ? 'Checking...' : 'Check transaction'}
      </button>
    </form>
  )
}