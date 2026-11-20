const API = "/api/v1"

async function api(path, options = {}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  })

  if (!res.ok) {
    let detail = `HTTP ${res.status}`
    try {
      const body = await res.json()
      if (typeof body.detail === "string") {
        detail = body.detail
      } else if (Array.isArray(body.detail)) {
        detail = body.detail.map((e) => e.msg).join("; ")
      }
    } catch {
      /* тело не JSON — оставляем код */
    }
    throw new Error(detail)
  }

  if (res.status === 204) return null
  return res.json()
}

function showMessage(el, text, type) {
  el.textContent = text
  el.className = `message ${type}`
}

function clearMessage(el) {
  el.textContent = ""
  el.className = "message"
}

function setLoading(button, loading, label) {
  if (loading) {
    button.dataset.label = button.textContent
    button.innerHTML = `<span class="spinner"></span> ${label}`
    button.disabled = true
  } else {
    button.textContent = button.dataset.label || label
    button.disabled = false
  }
}

function escapeHtml(value) {
  return String(value ?? "").replace(
    /[&<>"']/g,
    (ch) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch],
  )
}
