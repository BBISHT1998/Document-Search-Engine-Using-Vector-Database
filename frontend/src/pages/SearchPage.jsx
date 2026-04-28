import { useState } from 'react'
import { Search, Zap, AlertCircle } from 'lucide-react'
import client from '../api/client'
import ResultCard from '../components/ResultCard'

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [meta, setMeta] = useState(null)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError('')
    setResults([])
    try {
      const { data } = await client.get('/search/', { params: { q: query, limit: 8 } })
      setResults(data.results)
      setMeta({ time: data.search_time_ms, total: data.total_results })
      setSearched(true)
    } catch (err) {
      setError(err.response?.data?.detail || 'Search failed. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 860, margin: '0 auto' }}>
      <div className="page-header">
        <h1>🔍 Semantic Search</h1>
        <p>Search across your documents by meaning — not just keywords</p>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} style={{ display: 'flex', gap: 12, marginBottom: 32 }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <Search size={18} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            className="input"
            style={{ paddingLeft: 44, fontSize: '1rem', height: 52 }}
            placeholder='Try: "what is gradient descent?" or "machine learning applications"'
            value={query}
            onChange={e => setQuery(e.target.value)}
            autoFocus
          />
        </div>
        <button className="btn btn-primary" style={{ height: 52, paddingInline: 28 }} disabled={loading || !query.trim()}>
          {loading ? <div className="spinner" /> : <><Zap size={16} /> Search</>}
        </button>
      </form>

      {/* Error */}
      {error && (
        <div className="card fade-in" style={{ padding: '16px 20px', marginBottom: 24, borderColor: 'rgba(239,68,68,0.4)', display: 'flex', gap: 10, alignItems: 'center' }}>
          <AlertCircle size={18} color="var(--danger)" />
          <span style={{ color: 'var(--danger)', fontSize: '0.9rem' }}>{error}</span>
        </div>
      )}

      {/* Meta */}
      {meta && !loading && (
        <div style={{ marginBottom: 20, display: 'flex', gap: 16, alignItems: 'center' }}>
          <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            {meta.total} result{meta.total !== 1 ? 's' : ''} in {meta.time}ms
          </span>
          {meta.total === 0 && (
            <span className="badge badge-warning">No documents matched the similarity threshold</span>
          )}
        </div>
      )}

      {/* Results */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {results.map((r, i) => <ResultCard key={r.chunk_id} result={r} index={i} />)}
      </div>

      {/* Empty State */}
      {searched && results.length === 0 && !loading && !error && (
        <div className="card fade-in" style={{ padding: 48, textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>🔎</div>
          <h3 style={{ marginBottom: 8 }}>No matching documents found</h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Try a different query, or upload documents related to your topic.
          </p>
        </div>
      )}

      {/* Welcome State */}
      {!searched && !loading && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginTop: 8 }}>
          {[
            { emoji: '🧠', title: 'Semantic Understanding', desc: 'Finds documents by meaning, not just word matching' },
            { emoji: '⚡', title: 'Lightning Fast', desc: 'Vector similarity search returns results in milliseconds' },
            { emoji: '📊', title: 'Relevance Scored', desc: 'Every result shows exactly how relevant it is to your query' },
          ].map(({ emoji, title, desc }) => (
            <div key={title} className="card" style={{ padding: 24, textAlign: 'center' }}>
              <div style={{ fontSize: 32, marginBottom: 12 }}>{emoji}</div>
              <h3 style={{ fontSize: '0.95rem', marginBottom: 6 }}>{title}</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem' }}>{desc}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
