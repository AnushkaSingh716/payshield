import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import ScamChecker from './pages/ScamChecker'

const TABS = [
  { id: 'dashboard', label: 'Fraud Detector' },
  { id: 'scam', label: 'Scam Checker' },
]

// Headline text for each page
const HERO = {
  dashboard: {
    before: 'Spot sketchy payments',
    highlight: 'before they spot you',
    sub: 'Drop in a transaction. Our AI vibe-checks it in a second.',
  },
  scam: {
    before: 'Got a weird text?',
    highlight: 'Paste it, we will check it',
    sub: 'Fake KYC, lottery, UPI refund and OTP scams get caught here.',
  },
}

export default function App() {
  const [page, setPage] = useState('dashboard')
  const hero = HERO[page]

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Glowing colour blobs floating in the background */}
      <div className="pointer-events-none absolute -left-24 -top-24 h-96 w-96 animate-blob rounded-full bg-violet-600/40 blur-3xl" />
      <div className="pointer-events-none absolute -right-24 top-1/3 h-96 w-96 animate-blob rounded-full bg-pink-500/30 blur-3xl [animation-delay:-4s]" />
      <div className="pointer-events-none absolute bottom-0 left-1/3 h-96 w-96 animate-blob rounded-full bg-cyan-500/25 blur-3xl [animation-delay:-8s]" />

      <header className="relative z-10 mx-auto max-w-6xl px-4 pt-8">
        <div className="glass flex flex-wrap items-center justify-between gap-3 px-5 py-4">
          <h1 className="text-2xl font-bold tracking-tight">
            <span className="gradient-text">PayShield</span>
          </h1>

          <nav className="flex gap-2">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setPage(tab.id)}
                className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                  page === tab.id
                    ? 'bg-white/15 text-white shadow-[0_0_18px_rgba(167,139,250,0.35)]'
                    : 'text-violet-200 hover:bg-white/10'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="mt-10 text-center">
          <h2 className="text-4xl font-bold sm:text-5xl">
            {hero.before} <span className="gradient-text">{hero.highlight}</span>
          </h2>
          <p className="mt-3 text-violet-200/80">{hero.sub}</p>
        </div>
      </header>

      {/* Both pages stay loaded, so you don't lose your results when switching tabs */}
      <main className="relative z-10 mx-auto max-w-6xl px-4 py-8">
        <div className={page === 'dashboard' ? '' : 'hidden'}>
          <Dashboard />
        </div>
        <div className={page === 'scam' ? '' : 'hidden'}>
          <ScamChecker />
        </div>
      </main>
    </div>
  )
}