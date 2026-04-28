import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Database, Mail, Lock, User, Eye, EyeOff, AlertCircle } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [form, setForm] = useState({ username: '', email: '', password: '' })
  const [showPw, setShowPw] = useState(false)
  const [error, setError] = useState('')
  const { login, register, loading } = useAuth()
  const navigate = useNavigate()

  const update = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    const result = mode === 'login'
      ? await login(form.email, form.password)
      : await register(form.username, form.email, form.password)
    if (result.success) navigate('/search')
    else setError(result.error)
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center',
      justifyContent: 'center', padding: 24, position: 'relative', zIndex: 1,
    }}>
      <div style={{ width: '100%', maxWidth: 420 }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <div style={{
            width: 64, height: 64, borderRadius: 18, margin: '0 auto 16px',
            background: 'linear-gradient(135deg, var(--accent), var(--accent-dark))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 8px 32px var(--accent-glow)',
          }}>
            <Database size={30} color="#fff" />
          </div>
          <h1 style={{ fontSize: '1.8rem', marginBottom: 6 }}>DocSearch</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            {mode === 'login' ? 'Sign in to your account' : 'Create your account'}
          </p>
        </div>

        {/* Card */}
        <div className="card" style={{ padding: 32 }}>
          {/* Mode toggle */}
          <div style={{ display: 'flex', background: 'var(--glass)', borderRadius: 'var(--radius-md)', padding: 4, marginBottom: 28 }}>
            {['login', 'register'].map(m => (
              <button key={m} onClick={() => { setMode(m); setError('') }}
                style={{
                  flex: 1, padding: '8px 0', border: 'none', borderRadius: 'var(--radius-sm)', cursor: 'pointer',
                  fontSize: '0.88rem', fontWeight: 600, fontFamily: 'Inter, sans-serif',
                  background: mode === m ? 'linear-gradient(135deg,var(--accent),var(--accent-dark))' : 'transparent',
                  color: mode === m ? '#fff' : 'var(--text-muted)',
                  transition: 'var(--transition)',
                }}>
                {m === 'login' ? 'Sign In' : 'Register'}
              </button>
            ))}
          </div>

          <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            {mode === 'register' && (
              <div style={{ position: 'relative' }}>
                <User size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input className="input" style={{ paddingLeft: 42 }} placeholder="Username" value={form.username} onChange={update('username')} required />
              </div>
            )}

            <div style={{ position: 'relative' }}>
              <Mail size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input className="input" style={{ paddingLeft: 42 }} type="email" placeholder="Email address" value={form.email} onChange={update('email')} required />
            </div>

            <div style={{ position: 'relative' }}>
              <Lock size={16} style={{ position: 'absolute', left: 14, top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
              <input className="input" style={{ paddingLeft: 42, paddingRight: 42 }} type={showPw ? 'text' : 'password'} placeholder="Password" value={form.password} onChange={update('password')} required />
              <button type="button" onClick={() => setShowPw(!showPw)}
                style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
              </button>
            </div>

            {error && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--danger)', fontSize: '0.85rem', padding: '10px 14px', background: 'rgba(239,68,68,0.1)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(239,68,68,0.2)' }}>
                <AlertCircle size={15} /> {error}
              </div>
            )}

            <button className="btn btn-primary" type="submit" disabled={loading} style={{ marginTop: 4, height: 46, justifyContent: 'center' }}>
              {loading ? <div className="spinner" /> : mode === 'login' ? 'Sign In' : 'Create Account'}
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: 20, fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            {mode === 'login' ? 'No account? ' : 'Already have an account? '}
            <button onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}
              style={{ background: 'none', border: 'none', color: 'var(--accent-light)', cursor: 'pointer', fontWeight: 600, fontFamily: 'Inter' }}>
              {mode === 'login' ? 'Register' : 'Sign In'}
            </button>
          </p>
        </div>

        <p style={{ textAlign: 'center', marginTop: 20, fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          💡 First registered user automatically becomes admin
        </p>
      </div>
    </div>
  )
}
