import Dashboard from './pages/Dashboard'

export default function App() {
  return (
    <div className="min-h-screen bg-slate-100 text-slate-800">
      <header className="bg-slate-900 text-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <h1 className="text-xl font-bold">🛡️ PayShield</h1>
          <span className="text-sm text-slate-300">Fraud detection dashboard</span>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">
        <Dashboard />
      </main>
    </div>
  )
}