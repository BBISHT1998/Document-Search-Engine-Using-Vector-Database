import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from './context/AuthContext'
import Sidebar from './components/Sidebar'
import SearchPage from './pages/SearchPage'
import ChatPage from './pages/ChatPage'
import DocumentsPage from './pages/DocumentsPage'
import LoginPage from './pages/LoginPage'
import './index.css'

function AppLayout() {
  return (
    <div className="layout">
      <Sidebar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Navigate to="/search" replace />} />
          <Route path="/search"    element={<SearchPage />} />
          <Route path="/chat"      element={<ChatPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
          <Route path="/login"     element={<LoginPage />} />
          <Route path="*"          element={<Navigate to="/search" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppLayout />
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#1a1a2e',
              color: '#f0f0ff',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 12,
              fontFamily: 'Inter, sans-serif',
              fontSize: '0.88rem',
            },
            success: { iconTheme: { primary: '#22c55e', secondary: '#0a0a0f' } },
            error:   { iconTheme: { primary: '#ef4444', secondary: '#0a0a0f' } },
          }}
        />
      </AuthProvider>
    </BrowserRouter>
  )
}
