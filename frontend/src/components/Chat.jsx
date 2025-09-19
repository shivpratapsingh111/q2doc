import { useEffect, useRef, useState } from 'react'
import { PaperAirplaneIcon } from '@heroicons/react/24/solid'
import { PaperClipIcon } from '@heroicons/react/24/outline'
import { sendPrompt, uploadFile } from '../lib/api'

function Message({ role, content, typing, sources }) {
  const isUser = role === 'user'
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap shadow-sm ${
        isUser
          ? 'bg-emerald-600 text-white rounded-br-none'
          : 'bg-zinc-800 text-zinc-100 rounded-bl-none'
      }`}>
        {typing ? 'Thinking…' : content}
        {!isUser && sources && sources.length > 0 && (
          <div className="mt-3 pt-2 border-t border-zinc-700 text-xs text-zinc-300">
            <div className="mb-1 text-zinc-400">Sources</div>
            <div className="flex flex-wrap gap-2">
              {sources.map((s, i) => (
                <span key={i} className="inline-flex items-center gap-1 rounded-full bg-zinc-700/60 px-2 py-1">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  {s}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default function Chat({ chat, onUpdate, onRename, onSession }) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const fileRef = useRef(null)
  const listRef = useRef(null)

  const messages = chat?.messages || []
  const activeSession = chat?.sessionId || null
  const fileMeta = chat?.fileMeta || null

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages])

  // Removed auto-seeding message on fileMeta change to avoid duplicates

  const handleAttachClick = () => fileRef.current?.click()

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (file.type !== 'application/pdf') {
      onUpdate?.({ messages: [...messages, { role: 'assistant', content: 'Please select a PDF file.' }] })
      return
    }

    setUploading(true)
    setProgress(0)
    try {
      const { data } = await uploadFile(file, (loaded, total) => setProgress(Math.round((loaded / total) * 100)))
      if (data?.success) {
        const meta = { filename: data.data.filename, size: data.data.size }
        onSession?.(data.data.session_id, meta)
        onUpdate?.({
          sessionId: data.data.session_id,
          fileMeta: meta,
          messages: [{ role: 'assistant', content: `I've processed ${data.data.filename}. What would you like to know?` }]
        })
      } else {
        throw new Error(data?.message || 'Upload failed')
      }
    } catch (err) {
      onUpdate?.({ messages: [...messages, { role: 'assistant', content: `Upload error: ${err.message}` }] })
    } finally {
      setUploading(false)
      setProgress(0)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!activeSession || !input.trim()) return

    const userMsg = { role: 'user', content: input }
    onUpdate?.({ messages: [...messages, userMsg, { role: 'assistant', content: '', typing: true }] })
    setInput('')
    setLoading(true)

    try {
      const { data } = await sendPrompt(activeSession, userMsg.content)
      const answer = data?.data?.response?.answer || data?.data?.answer || 'No answer received'
      const sources = data?.data?.response?.source_file || data?.data?.source_file || []
      const next = [...messages, userMsg, { role: 'assistant', content: answer, sources }]
      onUpdate?.({ messages: next, preview: userMsg.content.slice(0, 60) })
      if (!chat?.title || chat.title === 'New chat') {
        onRename?.(userMsg.content.slice(0, 30))
      }
    } catch (err) {
      const next = [...messages]
      // replace typing with error
      next.push({ role: 'user', content: userMsg.content })
      next.push({ role: 'assistant', content: `Sorry, an error occurred: ${err.message}` })
      onUpdate?.({ messages: next })
    } finally {
      setLoading(false)
    }
  }

  const showOnlyBar = messages.length === 0

  return (
    <div className="relative flex-1 w-full flex flex-col overflow-hidden">
      {!showOnlyBar && (
        <div ref={listRef} className="flex-1 overflow-y-auto space-y-4 pr-1 scrollbar-thin py-6 pb-28">
          {messages.map((m, idx) => (
            <Message key={idx} role={m.role} content={m.content} typing={m.typing} sources={m.sources} />
          ))}
        </div>
      )}

      <div className={`w-full flex justify-center px-2 absolute bottom-0 left-0 right-0 bg-gradient-to-t from-zinc-900 via-zinc-900/95 to-transparent pt-3 pb-4`}>
        <form onSubmit={onSubmit} className="w-full sm:w-[700px] flex items-center gap-2">
          <input type="file" ref={fileRef} accept="application/pdf" className="hidden" onChange={handleFileChange} />

          <button
            type="button"
            onClick={handleAttachClick}
            disabled={uploading}
            title="Attach PDF"
            className="shrink-0 inline-flex items-center justify-center w-10 h-10 rounded-full border border-zinc-800 hover:bg-zinc-800 disabled:opacity-50"
          >
            <PaperClipIcon className="w-5 h-5" />
          </button>

          <div className="flex-1 relative">
            <input
              type="text"
              className="w-full p-3.5 rounded-2xl border border-zinc-800 bg-zinc-900 placeholder-zinc-500 focus:ring-2 focus:ring-emerald-500 focus:border-transparent disabled:opacity-50 text-zinc-100"
              placeholder={activeSession ? 'Ask anything about your document…' : 'Attach a PDF to start chatting'}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={!activeSession || loading}
            />

            {uploading && (
              <div className="absolute inset-0 bg-zinc-900/60 rounded-2xl flex items-center">
                <div className="w-full mx-3 h-1.5 rounded-full bg-zinc-800 overflow-hidden">
                  <div className="h-1.5 bg-emerald-500" style={{ width: `${progress}%` }} />
                </div>
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={!activeSession || loading || !input.trim()}
            className="shrink-0 inline-flex items-center gap-2 bg-white text-zinc-900 hover:bg-zinc-200 disabled:opacity-50 px-4 py-2 rounded-2xl"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
            <span className="hidden sm:inline">Send</span>
          </button>
        </form>
      </div>
    </div>
  )
}
