import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, X, CheckCircle, AlertCircle, Loader } from 'lucide-react'
import client from '../api/client'
import toast from 'react-hot-toast'

export default function FileUpload({ onUploadSuccess }) {
  const [files, setFiles] = useState([])

  const onDrop = useCallback((accepted) => {
    const newFiles = accepted.map(f => ({
      file: f,
      status: 'pending', // pending | uploading | success | error
      message: '',
    }))
    setFiles(prev => [...prev, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'], 'text/plain': ['.txt'] },
    maxSize: 50 * 1024 * 1024,
  })

  const uploadAll = async () => {
    for (let i = 0; i < files.length; i++) {
      if (files[i].status !== 'pending') continue
      setFiles(prev => prev.map((f, idx) => idx === i ? { ...f, status: 'uploading' } : f))

      const form = new FormData()
      form.append('file', files[i].file)

      try {
        const { data } = await client.post('/documents/upload', form, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        setFiles(prev => prev.map((f, idx) => idx === i
          ? { ...f, status: 'success', message: `${data.total_chunks} chunks indexed` }
          : f
        ))
        toast.success(`"${files[i].file.name}" indexed successfully!`)
        onUploadSuccess?.()
      } catch (err) {
        const msg = err.response?.data?.detail || 'Upload failed'
        setFiles(prev => prev.map((f, idx) => idx === i ? { ...f, status: 'error', message: msg } : f))
        toast.error(`"${files[i].file.name}": ${msg}`)
      }
    }
  }

  const remove = (i) => setFiles(prev => prev.filter((_, idx) => idx !== i))

  const pending = files.filter(f => f.status === 'pending').length

  return (
    <div>
      {/* Dropzone */}
      <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
        <input {...getInputProps()} />
        <Upload size={36} color="var(--accent-light)" style={{ marginBottom: 12 }} />
        <h3 style={{ marginBottom: 6, color: 'var(--text-primary)' }}>
          {isDragActive ? 'Drop files here' : 'Drag & drop documents'}
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          PDF, DOCX, TXT — up to 50MB each
        </p>
        <button className="btn btn-ghost" style={{ marginTop: 16 }} type="button">
          Browse Files
        </button>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div style={{ marginTop: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
          {files.map((item, i) => (
            <div key={i} className="card" style={{ padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
              <File size={18} color="var(--accent-light)" style={{ flexShrink: 0 }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {item.file.name}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {(item.file.size / 1024).toFixed(1)} KB
                  {item.message && ` · ${item.message}`}
                </div>
              </div>
              {/* Status icon */}
              {item.status === 'pending'   && <div style={{ width: 18 }} />}
              {item.status === 'uploading' && <div className="spinner" />}
              {item.status === 'success'   && <CheckCircle size={18} color="var(--success)" />}
              {item.status === 'error'     && <AlertCircle size={18} color="var(--danger)" />}
              {item.status === 'pending' && (
                <button onClick={() => remove(i)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}>
                  <X size={16} />
                </button>
              )}
            </div>
          ))}

          {pending > 0 && (
            <button className="btn btn-primary" style={{ marginTop: 8 }} onClick={uploadAll}>
              <Upload size={16} />
              Upload {pending} File{pending !== 1 ? 's' : ''}
            </button>
          )}
        </div>
      )}
    </div>
  )
}
