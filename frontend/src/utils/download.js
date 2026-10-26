import { apiFetch } from './api'

const parseFilename = (res, fallback) => {
  const cd = res.headers.get('Content-Disposition') || ''
  const m = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(cd)
  if (m && m[1]) { try { return decodeURIComponent(m[1]) } catch { return m[1] } }
  return fallback
}

export async function apiDownload(url, fallbackName = 'download') {
  try {
    const res = await apiFetch(url)
    if (!res.ok) {
      if (res.status === 401 || res.status === 403) return
      throw new Error(`下载失败 (${res.status})`)
    }
    const blob = await res.blob()
    const name = parseFilename(res, fallbackName)
    const href = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = href; a.download = name
    document.body.appendChild(a); a.click(); a.remove()
    setTimeout(() => URL.revokeObjectURL(href), 1000)
  } catch (e) {
    console.error('[apiDownload]', e)
    window.dispatchEvent(new CustomEvent('api:global-error', {
      detail: { message: e.message || '下载失败', status: -1 }
    }))
  }
}
