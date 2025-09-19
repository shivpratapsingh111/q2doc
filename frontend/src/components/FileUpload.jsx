import { useRef, useState } from 'react'
import { ArrowUpTrayIcon, DocumentIcon } from '@heroicons/react/24/outline'
import { uploadFile } from '../lib/api'

export default function FileUpload({ onUploaded }) {
  const inputRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('idle') // idle | uploading | done | error
  const [message, setMessage] = useState('')
  const [selected, setSelected] = useState(null)

  const onSelect = (file) => {
    if (!file) return
    if (file.type !== 'application/pdf') {
      setMessage('Please select a PDF file')
      setStatus('error')
      return
    }
    setSelected(file)
    setMessage('Ready to upload')
    setStatus('idle')
  }

  const handleInput = (e) => onSelect(e.target.files?.[0])

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files?.[0]
    onSelect(file)
  }

  const startUpload = async () => {
    if (!selected) return
    setStatus('uploading')
    setProgress(0)

    try {
      const { data } = await uploadFile(selected, (loaded, total) => {
        const pct = Math.round((loaded / total) * 100)
        setProgress(pct)
      })

      if (data?.success) {
        setStatus('done')
        setMessage('Uploaded successfully')
        onUploaded?.(data.data.session_id, { filename: data.data.filename, size: data.data.size })
      } else {
        throw new Error(data?.message || 'Upload failed')
      }
    } catch (err) {
      setStatus('error')
      setMessage(err.message)
    }
  }

  return (
    <div>
      <h2 className="text-xl font-semibold text-slate-800">Upload Document</h2>
      <p className="text-sm text-slate-500 mt-1">Drag & drop a PDF or click to choose</p>

      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        className={`mt-4 border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer ${dragOver ? 'border-blue-400 bg-blue-50' : 'border-slate-200'}`}
        onClick={() => inputRef.current?.click()}
      >
        <input ref={inputRef} type="file" accept="application/pdf" className="hidden" onChange={handleInput} />
        <DocumentIcon className="w-10 h-10 mx-auto text-red-500" />
        <p className="text-slate-600 mt-3">{selected ? selected.name : 'Drop PDF here or click to browse'}</p>
        {selected && <p className="text-xs text-slate-400 mt-1">{(selected.size/1024/1024).toFixed(2)} MB</p>}

        {status === 'uploading' && (
          <div className="w-full bg-slate-100 rounded-full h-2 mt-5">
            <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
          </div>
        )}

        {message && (
          <div className={`mt-4 text-sm ${status === 'error' ? 'text-red-600' : status === 'done' ? 'text-green-600' : 'text-slate-500'}`}>{message}</div>
        )}

        <button
          onClick={(e) => { e.stopPropagation(); startUpload() }}
          disabled={!selected || status === 'uploading'}
          className="mt-5 inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg"
        >
          <ArrowUpTrayIcon className="w-5 h-5" />
          Upload
        </button>
      </div>
    </div>
  )
}
