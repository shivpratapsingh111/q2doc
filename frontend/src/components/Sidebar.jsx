import { useMemo } from 'react'
import { PlusIcon, TrashIcon, ChevronDoubleLeftIcon, ChevronDoubleRightIcon } from '@heroicons/react/24/outline'

export default function Sidebar({ chats, activeId, onNewChat, onSelectChat, onDeleteChat, collapsed = false, onToggle }) {
  const sorted = useMemo(() => {
    return [...(chats || [])].sort((a, b) => (b.updatedAt || b.createdAt) - (a.updatedAt || a.createdAt))
  }, [chats])

  const widthClasses = collapsed ? 'md:w-16 lg:w-16 xl:w-16' : 'md:w-64 lg:w-72 xl:w-80'

  return (
    <aside className={`hidden md:flex ${widthClasses} flex-col border-r border-zinc-800 bg-zinc-950/60 text-zinc-200`}> 
      <div className={`p-3 border-b border-zinc-800 flex ${collapsed ? 'flex-col items-stretch gap-2' : 'items-center gap-2'} min-w-0`}>
        {collapsed ? (
          <>
            <button
              onClick={onToggle}
              className="inline-flex items-center justify-center rounded-md border border-zinc-800 hover:bg-zinc-900 w-full py-2"
              title="Expand"
            >
              <ChevronDoubleRightIcon className="w-4 h-4" />
            </button>
            <button
              onClick={onNewChat}
              className="inline-flex items-center justify-center gap-2 rounded-md bg-zinc-800 hover:bg-zinc-700 text-zinc-100 w-full py-2"
              title="New chat"
            >
              <PlusIcon className="w-4 h-4" />
            </button>
          </>
        ) : (
          <>
            <button
              onClick={onNewChat}
              className="inline-flex items-center justify-center gap-2 rounded-md bg-zinc-800 hover:bg-zinc-700 text-zinc-100 px-3 py-2 text-sm flex-1 min-w-0"
              title="New chat"
            >
              <PlusIcon className="w-4 h-4 shrink-0" />
              <span className="truncate">New chat</span>
            </button>
            <button
              onClick={onToggle}
              className="inline-flex items-center justify-center rounded-md border border-zinc-800 hover:bg-zinc-900 ml-auto px-2 py-2"
              title="Collapse"
            >
              <ChevronDoubleLeftIcon className="w-4 h-4" />
            </button>
          </>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-thin">
        {sorted.length === 0 && !collapsed && (
          <div className="text-xs text-zinc-500 px-2 py-3">No chats yet. Start a new one.</div>
        )}
        {sorted.map((c) => (
          <div
            key={c.id}
            className={`group flex items-center ${collapsed ? 'justify-center' : 'gap-2'} rounded-md ${collapsed ? 'px-1' : 'px-2'} py-2 cursor-pointer ${
              activeId === c.id ? 'bg-zinc-800 text-zinc-100' : 'hover:bg-zinc-900 text-zinc-300'
            }`}
            onClick={() => onSelectChat?.(c.id)}
            title={collapsed ? (c.title || 'Untitled chat') : undefined}
          >
            {collapsed ? (
              <div className={`h-2 w-2 rounded-full ${activeId === c.id ? 'bg-emerald-400' : 'bg-zinc-500'}`} />
            ) : (
              <>
                <div className="flex-1 min-w-0">
                  <div className="truncate text-sm">{c.title || 'Untitled chat'}</div>
                  <div className="truncate text-[10px] text-zinc-500">
                    {c.fileMeta?.filename || c.preview || ''}
                  </div>
                </div>
                <button
                  title="Delete chat"
                  onClick={(e) => { e.stopPropagation(); onDeleteChat?.(c.id) }}
                  className="opacity-0 group-hover:opacity-100 rounded p-1 text-zinc-400 hover:text-red-400 hover:bg-zinc-800"
                >
                  <TrashIcon className="w-4 h-4" />
                </button>
              </>
            )}
          </div>
        ))}
      </div>
    </aside>
  )
}
