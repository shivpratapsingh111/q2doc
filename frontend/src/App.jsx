import { useEffect, useMemo, useRef, useState } from 'react'
import Chat from './components/Chat.jsx'
import Sidebar from './components/Sidebar.jsx'

function App() {
  // Sidebar collapse (persisted)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    try {
      return localStorage.getItem('sidebarCollapsed') === 'true'
    } catch {
      return false
    }
  })
  const toggleSidebar = () => {
    setSidebarCollapsed(prev => {
      const next = !prev
      localStorage.setItem('sidebarCollapsed', String(next))
      return next
    })
  }

  // Chats state (persisted)
  const [chats, setChats] = useState(() => {
    try {
      const raw = localStorage.getItem('chats')
      return raw ? JSON.parse(raw) : []
    } catch {
      return []
    }
  })
  const [activeId, setActiveId] = useState(() => {
    try {
      return localStorage.getItem('activeChatId') || null
    } catch {
      return null
    }
  })

  useEffect(() => {
    localStorage.setItem('chats', JSON.stringify(chats))
  }, [chats])
  useEffect(() => {
    if (activeId) localStorage.setItem('activeChatId', activeId)
  }, [activeId])

  const activeChat = useMemo(() => chats.find(c => c.id === activeId) || null, [chats, activeId])

  const createChat = () => {
    const id = `chat_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
    const newChat = {
      id,
      title: 'New chat',
      messages: [],
      sessionId: null,
      fileMeta: null,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      preview: ''
    }
    setChats(prev => [newChat, ...prev])
    setActiveId(id)
  }

  const selectChat = (id) => setActiveId(id)

  const deleteChat = (id) => {
    setChats(prev => prev.filter(c => c.id !== id))
    if (activeId === id) {
      const remaining = chats.filter(c => c.id !== id)
      setActiveId(remaining[0]?.id || null)
    }
  }

  const updateChat = (id, patch) => {
    setChats(prev => prev.map(c => (c.id === id ? { ...c, ...patch, updatedAt: Date.now() } : c)))
  }

  // If there are no chats, create one at start (guard against StrictMode double invoke)
  const createdOnceRef = useRef(false)
  useEffect(() => {
    if (createdOnceRef.current) return
    if (chats.length === 0) {
      createChat()
    }
    createdOnceRef.current = true
  }, [])

  return (
    <div className="h-screen overflow-hidden flex bg-zinc-900 text-zinc-100">
      <Sidebar
        chats={chats}
        activeId={activeId}
        onNewChat={createChat}
        onSelectChat={selectChat}
        onDeleteChat={deleteChat}
        collapsed={sidebarCollapsed}
        onToggle={toggleSidebar}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="flex items-center justify-between px-4 sm:px-6 py-3 border-b border-zinc-800 bg-zinc-900 backdrop-blur">
          <div className="flex items-center gap-3 min-w-0">
            <div className="h-2 w-2 rounded-full bg-emerald-400 shrink-0" />
            <h1 className="text-sm font-medium text-zinc-300 shrink-0">Q2DOC</h1>
            {activeChat && (
              <ChatTitleEditor
                title={activeChat.title}
                onRename={(t) => updateChat(activeChat.id, { title: t })}
              />
            )}
          </div>
          <div />
        </header>

        <main className="flex-1 flex overflow-hidden">
          <div className="w-full max-w-4xl mx-auto px-2 sm:px-6 lg:px-10 py-2 h-full flex flex-col">
            {activeChat && (
              <Chat
                chat={activeChat}
                onUpdate={(patch) => updateChat(activeChat.id, patch)}
                onRename={(title) => updateChat(activeChat.id, { title })}
                onSession={(sessionId, fileMeta) => updateChat(activeChat.id, { sessionId, fileMeta })}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

function ChatTitleEditor({ title, onRename }) {
  const [editing, setEditing] = useState(false)
  const [val, setVal] = useState(title || 'New chat')
  useEffect(() => setVal(title || 'New chat'), [title])

  const commit = () => {
    const t = (val || 'New chat').trim()
    onRename?.(t)
    setEditing(false)
  }

  return (
    <div className="min-w-0">
      {editing ? (
        <input
          autoFocus
          value={val}
          onChange={(e) => setVal(e.target.value)}
          onBlur={commit}
          onKeyDown={(e) => { if (e.key === 'Enter') commit(); if (e.key === 'Escape') setEditing(false) }}
          className="bg-zinc-900 border border-zinc-700 rounded px-2 py-1 text-xs text-zinc-200 focus:outline-none focus:ring-1 focus:ring-emerald-500"
        />
      ) : (
        <button
          title="Rename chat"
          onClick={() => setEditing(true)}
          className="truncate max-w-[40vw] text-xs text-zinc-400 hover:text-zinc-200"
        >
          {title || 'New chat'}
        </button>
      )}
    </div>
  )
}

export default App
