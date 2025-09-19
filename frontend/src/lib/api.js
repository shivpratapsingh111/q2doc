const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export function uploadFile(file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('PUT', `${API_BASE_URL}/upload`)

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && typeof onProgress === 'function') {
        onProgress(e.loaded, e.total)
      }
    }

    xhr.onload = () => {
      try {
        const data = JSON.parse(xhr.responseText)
        resolve({ status: xhr.status, data })
      } catch (e) {
        reject(new Error('Failed to parse server response'))
      }
    }

    xhr.onerror = () => reject(new Error('Network error while uploading'))

    const form = new FormData()
    form.append('file', file)
    xhr.send(form)
  })
}

export async function sendPrompt(session_id, prompt) {
  const res = await fetch(`${API_BASE_URL}/prompt`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id, prompt })
  })
  const data = await res.json()
  if (!res.ok || data?.success === false) {
    throw new Error(data?.message || `HTTP ${res.status}`)
  }
  return { status: res.status, data }
}
