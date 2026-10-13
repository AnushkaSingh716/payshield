// All calls to the backend live here, so the rest of the app stays simple.
// VITE_API_URL comes from frontend/.env (Vite only exposes variables starting with VITE_).
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options) {
  const res = await fetch(`${API_URL}${path}`, options)

  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try {
      const data = await res.json()
      if (Array.isArray(data.detail)) {
        // Validation errors from FastAPI: show which field is wrong
        message = data.detail
          .map((e) => `${e.loc[e.loc.length - 1]}: ${e.msg}`)
          .join(', ')
      } else if (typeof data.detail === 'string') {
        message = data.detail
      }
    } catch {
      // response had no JSON body; keep the default message
    }
    throw new Error(message)
  }
  return res.json()
}

export function predictTransaction(data) {
  return request('/predict', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export function getTransactions(limit = 20) {
  return request(`/transactions?limit=${limit}`)
}

export function getStats() {
  return request('/stats')
}

export function checkMessage(text) {
  return request('/check-message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  })
}