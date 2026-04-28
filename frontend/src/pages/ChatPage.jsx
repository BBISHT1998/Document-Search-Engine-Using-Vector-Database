import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, FileText, Sparkles, Trash2 } from 'lucide-react'
import client from '../api/client'
import ReactMarkdown from 'react-markdown'

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "Hello! I'm your document assistant powered by Gemini AI. Ask me anything about your uploaded documents and I'll provide answers grounded in that content.",
      sources: [],
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async () => {
    if (!input.trim() || loading) return
    const question = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: question, sources: [] }])
    setLoading(true)

    try {
      const history = messages.slice(-6).map(m => ({ role: m.role, content: m.content }))
      const { data } = await client.post('/rag/chat', {
        question,
        conversation_history: history,
      })
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        sources: data.sources,
        has_answer: data.has_answer,
        response_time_ms: data.response_time_ms,
      }])
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `⚠️ Error: ${err.response?.data?.detail || 'Failed to get response. Is the backend running?'}`,
        sources: [],
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 64px)' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h1 style={{ fontSize: '1.6rem', display: 'flex', alignItems: 'center', gap: 10 }}>
            <Sparkles size={24} color="var(--accent-light)" /> AI Document Chat
          </h1>
          <p>Answers grounded in your uploaded documents</p>
        </div>
        <button className="btn btn-ghost" onClick={() => setMessages([{
          role: 'assistant',
          content: "Chat cleared! Ask me anything about your documents.",
          sources: [],
        }])}>
          <Trash2 size={15} /> Clear
        </button>
      </div>

      {/* Messages */}
      <div style={{
        flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column',
        gap: 16, paddingRight: 4, marginBottom: 16
      }}>
        {messages.map((msg, i) => (
          <div key={i} className="fade-in" style={{ display: 'flex', flexDirection: 'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
            {/* Avatar row */}
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 8, flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
              <div style={{
                width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
                background: msg.role === 'user' ? 'linear-gradient(135deg,var(--accent),var(--accent-dark))' : 'rgba(108,99,255,0.2)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                {msg.role === 'user' ? <User size={14} color="#fff" /> : <Bot size={14} color="var(--accent-light)" />}
              </div>

              <div className={`chat-bubble ${msg.role}`}>
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>
            </div>

            {/* Sources */}
            {msg.sources?.length > 0 && (
              <div style={{ marginTop: 8, marginLeft: 38, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {msg.sources.map((s, si) => (
                  <div key={si} style={{
                    display: 'flex', alignItems: 'center', gap: 5,
                    padding: '3px 10px', borderRadius: 999,
                    background: 'rgba(108,99,255,0.1)', border: '1px solid rgba(108,99,255,0.2)',
                    fontSize: '0.72rem', color: 'var(--text-secondary)',
                  }}>
                    <FileText size={11} color="var(--accent-light)" />
                    {s.document_name} {s.page_number ? `· p.${s.page_number}` : ''} · {Math.round(s.similarity_score * 100)}%
                  </div>
                ))}
              </div>
            )}

            {/* Response time */}
            {msg.response_time_ms && (
              <div style={{ marginLeft: 38, marginTop: 4, fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                {msg.response_time_ms}ms
              </div>
            )}
          </div>
        ))}

        {/* Loading indicator */}
        {loading && (
          <div className="fade-in" style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
            <div style={{ width: 30, height: 30, borderRadius: '50%', background: 'rgba(108,99,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Bot size={14} color="var(--accent-light)" />
            </div>
            <div className="card" style={{ padding: '12px 16px', display: 'flex', gap: 6, alignItems: 'center' }}>
              <div className="spinner" style={{ width: 14, height: 14 }} />
              <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Searching documents & generating answer...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ display: 'flex', gap: 10 }}>
        <input
          className="input"
          style={{ height: 50 }}
          placeholder="Ask anything about your documents..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && send()}
          disabled={loading}
        />
        <button className="btn btn-primary" style={{ height: 50, width: 50, padding: 0, justifyContent: 'center' }} onClick={send} disabled={loading || !input.trim()}>
          <Send size={18} />
        </button>
      </div>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.72rem', marginTop: 6, textAlign: 'center' }}>
        Answers are grounded in your uploaded documents. Press Enter to send.
      </p>
    </div>
  )
}
