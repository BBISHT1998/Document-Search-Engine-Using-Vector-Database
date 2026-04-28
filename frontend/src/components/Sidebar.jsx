import { NavLink, useNavigate } from 'react-router-dom'
import { Search, MessageSquare, FileText, LogOut, Database, User } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

const links = [
  { to: '/search',    label: 'Search',    icon: Search },
  { to: '/chat',      label: 'AI Chat',   icon: MessageSquare },
  { to: '/documents', label: 'Documents', icon: FileText },
]

export default function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="sidebar">
      {/* Logo */}
      <div style={{ padding: '8px 14px 24px', borderBottom: '1px solid var(--glass-border)', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg, var(--accent), var(--accent-dark))',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 15px var(--accent-glow)'
          }}>
            <Database size={18} color="#fff" />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>DocSearch</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Vector Engine</div>
          </div>
        </div>
      </div>

      {/* Nav Links */}
      {links.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
        >
          <Icon size={17} />
          {label}
        </NavLink>
      ))}

      {/* Spacer */}
      <div style={{ flex: 1 }} />
      <div className="divider" />

      {/* User Info */}
      {user ? (
        <>
          <div style={{
            padding: '10px 14px',
            background: 'var(--glass)',
            borderRadius: 'var(--radius-md)',
            marginBottom: 8,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{
                width: 28, height: 28, borderRadius: '50%',
                background: 'linear-gradient(135deg, var(--accent), #3b82f6)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '0.75rem', fontWeight: 700,
              }}>
                {user.username?.[0]?.toUpperCase()}
              </div>
              <div>
                <div style={{ fontSize: '0.82rem', fontWeight: 600 }}>{user.username}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{user.role}</div>
              </div>
            </div>
          </div>
          <button className="nav-link" onClick={() => { logout(); navigate('/login') }}>
            <LogOut size={17} />
            Sign Out
          </button>
        </>
      ) : (
        <NavLink to="/login" className="nav-link">
          <User size={17} />
          Sign In
        </NavLink>
      )}
    </div>
  )
}
