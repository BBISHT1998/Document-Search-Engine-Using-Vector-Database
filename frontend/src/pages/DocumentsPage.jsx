import { useState, useEffect } from 'react'
import { FileText, Trash2, Upload, RefreshCw, Database } from 'lucide-react'
import client from '../api/client'
import FileUpload from '../components/FileUpload'
import toast from 'react-hot-toast'

function StatusBadge({ status }) {
  const map = { indexed: 'badge-success', processing: 'badge-warning', failed: 'badge-danger' }
  return <span className={`badge ${map[status] || 'badge-info'}`}>{status}</span>
}

export default function DocumentsPage() {
  const [docs, setDocs] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(null)

  const fetchDocs = async () => {
    setLoading(true)
    try {
      const [docsRes, statsRes] = await Promise.all([
        client.get('/documents/'),
        client.get('/documents/stats'),
      ])
      setDocs(docsRes.data.documents)
      setStats(statsRes.data)
    } catch {
      toast.error('Failed to load documents')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchDocs() }, [])

  const deleteDoc = async (id, name) => {
    if (!confirm(`Delete "${name}"? This removes it from the search index.`)) return
    setDeleting(id)
    try {
      await client.delete(`/documents/${id}`)
      toast.success(`"${name}" deleted`)
      fetchDocs()
    } catch {
      toast.error('Delete failed')
    } finally {
      setDeleting(null)
    }
  }

  const formatSize = (bytes) => bytes > 1024 * 1024 ? `${(bytes / 1024 / 1024).toFixed(1)} MB` : `${(bytes / 1024).toFixed(0)} KB`

  return (
    <div style={{ maxWidth: 900, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 32 }}>
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h1>📂 Documents</h1>
          <p>Upload and manage your document library</p>
        </div>
        <button className="btn btn-ghost" onClick={fetchDocs}>
          <RefreshCw size={15} /> Refresh
        </button>
      </div>

      {/* Stats Row */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12, marginBottom: 32 }}>
          {[
            { label: 'Documents', value: stats.total_documents, icon: FileText, color: 'var(--accent-light)' },
            { label: 'Chunks Indexed', value: stats.total_chunks.toLocaleString(), icon: Database, color: 'var(--success)' },
            { label: 'Total Queries', value: stats.total_queries, icon: RefreshCw, color: 'var(--info)' },
            { label: 'Avg Match Score', value: stats.avg_similarity_score ? `${(stats.avg_similarity_score * 100).toFixed(0)}%` : '—', icon: Upload, color: 'var(--warning)' },
          ].map(({ label, value, icon: Icon, color }) => (
            <div key={label} className="card" style={{ padding: '20px 20px' }}>
              <Icon size={20} color={color} style={{ marginBottom: 8 }} />
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color }}>{value}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 2 }}>{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Upload Section */}
      <div className="card" style={{ padding: 24, marginBottom: 32 }}>
        <h3 style={{ marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Upload size={18} color="var(--accent-light)" /> Upload Documents
        </h3>
        <FileUpload onUploadSuccess={fetchDocs} />
      </div>

      {/* Documents Table */}
      <div className="card" style={{ overflow: 'hidden' }}>
        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--glass-border)' }}>
          <h3>Library ({docs.length})</h3>
        </div>

        {loading ? (
          <div style={{ padding: 48, textAlign: 'center' }}>
            <div className="spinner" style={{ margin: '0 auto 12px', width: 28, height: 28 }} />
            <p style={{ color: 'var(--text-muted)' }}>Loading documents...</p>
          </div>
        ) : docs.length === 0 ? (
          <div style={{ padding: 48, textAlign: 'center' }}>
            <FileText size={40} color="var(--text-muted)" style={{ marginBottom: 12 }} />
            <p style={{ color: 'var(--text-muted)' }}>No documents uploaded yet</p>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--glass-border)' }}>
                {['Document', 'Type', 'Size', 'Chunks', 'Status', ''].map(h => (
                  <th key={h} style={{ padding: '12px 16px', textAlign: 'left', fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {docs.map((doc, i) => (
                <tr key={doc.id} className="fade-in" style={{ borderBottom: i < docs.length - 1 ? '1px solid rgba(255,255,255,0.04)' : 'none', transition: 'background 0.15s' }}
                  onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-card-hover)'}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '14px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <FileText size={16} color="var(--accent-light)" />
                      <span style={{ fontSize: '0.88rem', fontWeight: 500 }}>{doc.original_name}</span>
                    </div>
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <span className="badge badge-accent" style={{ textTransform: 'uppercase' }}>{doc.file_type}</span>
                  </td>
                  <td style={{ padding: '14px 16px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{formatSize(doc.file_size)}</td>
                  <td style={{ padding: '14px 16px', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>{doc.total_chunks}</td>
                  <td style={{ padding: '14px 16px' }}><StatusBadge status={doc.status} /></td>
                  <td style={{ padding: '14px 16px' }}>
                    <button
                      className="btn btn-danger"
                      style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                      onClick={() => deleteDoc(doc.id, doc.original_name)}
                      disabled={deleting === doc.id}
                    >
                      {deleting === doc.id ? <div className="spinner" style={{ width: 14, height: 14 }} /> : <Trash2 size={14} />}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
