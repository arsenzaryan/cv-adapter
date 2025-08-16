type AdaptRequest = {
  resume_text: string
  job_description: string
  strategy?: string
}

export async function adaptResume(payload: AdaptRequest): Promise<{ adapted_resume: string }> {
  const res = await fetch('/api/adapt', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Request failed with ${res.status}`)
  }
  return res.json()
}

export async function adaptResumeUpload(params: {
  file: File
  job_description: string
  strategy?: string
}): Promise<{ adapted_resume: string }> {
  const form = new FormData()
  form.append('file', params.file)
  form.append('job_description', params.job_description)
  if (params.strategy) form.append('strategy', params.strategy)

  const res = await fetch('/api/adapt-upload', {
    method: 'POST',
    body: form,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `Request failed with ${res.status}`)
  }
  return res.json()
}

export async function generatePdf(params: { text: string; filename?: string; title?: string }): Promise<Blob> {
  const form = new FormData()
  form.append('text', params.text)
  if (params.filename) form.append('filename', params.filename)
  if (params.title) form.append('title', params.title)

  const res = await fetch('/api/pdf', {
    method: 'POST',
    body: form,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(text || `PDF request failed with ${res.status}`)
  }
  return res.blob()
} 