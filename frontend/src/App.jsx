import Dashboard from './pages/Dashboard'

export default function App() {
  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Glowing colour blobs floating in the background */}
      <div className="pointer-events-none absolute -left-24 -top-24 h-96 w-96 animate-blob rounded-full bg-violet-600/40 blur-3xl" />
      <div className="pointer-events-none absolute -right-24 top-1/3 h-96 w-96 animate-blob rounded-full bg-pink-500/30 blur-3xl [animation-delay:-4s]" />
      <div className="pointer-events-none absolute bottom-0 left-1/3 h-96 w-96 animate-blob rounded-full bg-cyan-500/25 blur-3xl [animation-delay:-8s]" />

      <header className="relative z-10 mx-auto max-w-6xl px-4 pt-8">
        <div className="glass flex items-center justify-between px-5 py-4">
          <h1 className="text-2xl font-bold">
            🛡️ <span className="gradient-text">PayShield</span>
          </h1>
          <span className="hidden rounded-full border border-white/15 bg-white/5 px-3 py-1 text-sm text-violet-200 sm:inline">
            <span className="text-emerald-400">●</span> Live fraud radar
          </span>
        </div>

        <div className="mt-10 text-center">
          <h2 className="text-4xl font-bold sm:text-5xl">
            Spot sketchy payments{' '}
            <span className="gradient-text">before they spot you</span> 👀
          </h2>
          <p className="mt-3 text-violet-200/80">
            Drop in a transaction. Our AI vibe-checks it in a second.
          </p>
        </div>
      </header>

      <main className="relative z-10 mx-auto max-w-6xl px-4 py-8">
        <Dashboard />
      </main>
    </div>
  )
}