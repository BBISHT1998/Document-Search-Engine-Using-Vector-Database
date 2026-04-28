import { FileText, Star, ChevronRight } from 'lucide-react'

export default function ResultCard({ result, index }) {
  const { content, document_name, page_number, relevance_percent, similarity_score } = result

  const scoreColor = relevance_percent >= 80
    ? 'var(--success)'
    : relevance_percent >= 50
    ? 'var(--warning)'
    : 'var(--danger)'

  return (
    <div className="card fade-in" style={{
      padding: '20px 24px',
      animationDelay: `${index * 0.05}s`,
      cursor: 'default',
    }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: 'rgba(108,99,255,0.15)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <FileText size={16} color="var(--accent-light)" />
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
              {document_name}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              {page_number ? `Page ${page_number}` : 'Document'}
            </div>
          </div>
        </div>

        {/* Score Badge */}
        <div style={{ textAlign: 'right' }}>
          <div style={{
            display: 'flex', alignItems: 'center', gap: 4,
            color: scoreColor, fontWeight: 700, fontSize: '0.9rem'
          }}>
            <Star size={13} fill={scoreColor} />
            {relevance_percent}%
          </div>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>match</div>
        </div>
      </div>

      {/* Score bar */}
      <div className="score-bar" style={{ marginBottom: 14 }}>
        <div
          className="score-bar-fill"
          style={{ width: `${relevance_percent}%`, background: `linear-gradient(90deg, ${scoreColor}, var(--accent-light))` }}
        />
      </div>

      {/* Content */}
      <p style={{
        color: 'var(--text-secondary)',
        fontSize: '0.88rem',
        lineHeight: 1.7,
        display: '-webkit-box',
        WebkitLineClamp: 4,
        WebkitBoxOrient: 'vertical',
        overflow: 'hidden',
      }}>
        {content}
      </p>

      {/* Footer */}
      <div style={{ marginTop: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span className="badge badge-accent">Similarity: {similarity_score.toFixed(3)}</span>
        <ChevronRight size={16} color="var(--text-muted)" />
      </div>
    </div>
  )
}
