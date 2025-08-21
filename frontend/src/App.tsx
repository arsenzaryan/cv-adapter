import React, { useEffect, useRef, useState } from 'react'
import { adaptResumeUpload, adaptResume, generatePdf, fetchMe, loginWithGoogle, logout } from './api'

type ParsedBlock = {
  type: 'heading' | 'subheading' | 'meta' | 'paragraph' | 'list'
  text?: string
  items?: string[]
}

type ParsedSection = {
  blocks: ParsedBlock[]
}

function parseResultToSections(text: string): ParsedSection[] {
  const lines = text.split(/\r?\n/)
  const sections: ParsedSection[] = []
  let current: ParsedSection | null = null

  const startSection = () => {
    if (!current) current = { blocks: [] }
  }

  const pushSectionIfNotEmpty = () => {
    if (current && current.blocks.length) {
      sections.push(current)
      current = null
    }
  }

  const isBoldHeading = (line: string) => /^(?:##\s+|\*\*[^*]+\*\*)$/.test(line)
  const extractHeadingText = (line: string) => line.replace(/^##\s+/, '').replace(/^\*\*|\*\*$/g, '')
  const isItalicSolo = (line: string) => /^\*[^*]+\*$/.test(line)
  const extractItalicText = (line: string) => line.replace(/^\*|\*$/g, '')
  const isMetaDate = (line: string) => /(\b\d{4}\b\s*[–-]\s*(?:\b\d{4}\b|Present))|([A-Za-z]{3,9}\s+\d{4}\s*[–-]\s*(?:[A-Za-z]{3,9}\s+)?(?:\d{4}|Present))/i.test(line)
  const isBullet = (line: string) => /^[-•]\s+/.test(line)

  for (const raw of lines) {
    const line = raw.trim()
    if (!line) continue

    if (isBoldHeading(line)) {
      // New section on heading
      pushSectionIfNotEmpty()
      current = { blocks: [{ type: 'heading', text: extractHeadingText(line) }] }
      continue
    }

    if (!current) startSection()

    if (isItalicSolo(line)) {
      current!.blocks.push({ type: 'subheading', text: extractItalicText(line) })
      continue
    }

    if (isMetaDate(line)) {
      current!.blocks.push({ type: 'meta', text: line })
      continue
    }

    if (isBullet(line)) {
      const itemText = line.replace(/^[-•]\s+/, '')
      const last = current!.blocks[current!.blocks.length - 1]
      if (last && last.type === 'list') {
        last.items!.push(itemText)
      } else {
        current!.blocks.push({ type: 'list', items: [itemText] })
      }
      continue
    }

    // Default paragraph
    current!.blocks.push({ type: 'paragraph', text: line })
  }

  pushSectionIfNotEmpty()
  return sections.length ? sections : [{ blocks: [{ type: 'paragraph', text }] }]
}

function renderInlineEmphasis(text: string): React.ReactNode[] {
  const nodes: React.ReactNode[] = []
  const regex = /(\*\*[^*]+?\*\*|\*[^*\s][^*]*?\*)/g
  let lastIndex = 0
  let match: RegExpExecArray | null
  let key = 0
  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) nodes.push(text.slice(lastIndex, match.index))
    const token = match[0]
    if (token.startsWith('**')) nodes.push(<strong key={key++}>{token.slice(2, -2)}</strong>)
    else nodes.push(<em key={key++}>{token.slice(1, -1)}</em>)
    lastIndex = regex.lastIndex
  }
  if (lastIndex < text.length) nodes.push(text.slice(lastIndex))
  return nodes
}

export default function App() {
  const [mode, setMode] = useState<'upload' | 'paste'>('upload')
  const [file, setFile] = useState<File | null>(null)
  const [resumeText, setResumeText] = useState('')
  const [jobDescription, setJobDescription] = useState('')
  const [strategy, setStrategy] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState('')
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const [view, setView] = useState<'formatted' | 'plain'>('formatted')
  const [me, setMe] = useState<{ authenticated: boolean; email?: string; name?: string; picture?: string }>({ authenticated: false })

  const plainRef = useRef<HTMLTextAreaElement | null>(null)
  const autosizePlain = () => {
    const el = plainRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${el.scrollHeight}px`
  }
  useEffect(() => {
    if (view === 'plain') autosizePlain()
  }, [result, view])

  useEffect(() => {
    fetchMe().then(setMe).catch(() => setMe({ authenticated: false }))
  }, [])

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult('')
    setCopied(false)
    try {
      if (mode === 'upload') {
        if (!file) throw new Error('Please upload a PDF resume')
        const response = await adaptResumeUpload({
          file,
          job_description: jobDescription,
          strategy: strategy || undefined,
        })
        setResult(response.adapted_resume)
      } else {
        if (!resumeText.trim()) throw new Error('Please paste your resume text')
        const response = await adaptResume({
          resume_text: resumeText,
          job_description: jobDescription,
          strategy: strategy || undefined,
        })
        setResult(response.adapted_resume)
      }
    } catch (err: any) {
      setError(err?.message || 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  const onTab = (next: 'upload' | 'paste') => {
    setMode(next)
    setError('')
    setResult('')
    setCopied(false)
  }

  const onDropResume = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    const dropped = e.dataTransfer?.files?.[0]
    if (!dropped) return
    if (dropped.type !== 'application/pdf') {
      setError('Please drop a PDF file')
      return
    }
    setFile(dropped)
  }

  const onCopy = async () => {
    if (!result) return
    try {
      await navigator.clipboard.writeText(result)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      // ignore
    }
  }

  const onDownload = async () => {
    if (!result) return
    try {
      if (view === 'formatted') {
        const blob = await generatePdf({ text: result, filename: 'adapted-cv', title: 'Curriculum Vitae' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'adapted-cv.pdf'
        document.body.appendChild(a)
        a.click()
        a.remove()
        URL.revokeObjectURL(url)
      } else {
        const blob = new Blob([result], { type: 'text/plain;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'adapted-cv.txt'
        document.body.appendChild(a)
        a.click()
        a.remove()
        URL.revokeObjectURL(url)
      }
    } catch (err) {
      // silently ignore for now
    }
  }

  const onClear = () => {
    setResult('')
    setCopied(false)
  }

  const sections = view === 'formatted' && result ? parseResultToSections(result) : []

  return (
    <div className="app-container">
      <div className="page-header" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
        <div style={{ fontWeight: 800 }}>CV Adapter</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {me.authenticated ? (
            <>
              <span className="badge">Premium model enabled</span>
              {me.picture ? <img src={me.picture} alt="avatar" style={{ width: 24, height: 24, borderRadius: 999 }} /> : null}
              <span style={{ fontSize: 13, color: '#334155' }}>{me.name || me.email}</span>
              <button className="btn-secondary" onClick={async () => { await logout(); setMe({ authenticated: false }); }}>Logout</button>
            </>
          ) : (
            <>
              <button className="btn" onClick={() => loginWithGoogle()}>Sign up / Log in</button>
              <span className="badge">Login to access a better AI model (free)</span>
            </>
          )}
        </div>
      </div>

      <section className="hero">
        <h1 className="page-title">Adapt your CV for every opportunity</h1>
        <p className="lead">Make your experience resonate with each role. Paste the job description and we’ll refocus your CV to highlight what matters most—clearly, concisely, and ATS-friendly.</p>
        <div className="badges">
          <span className="badge">✓ ATS‑friendly</span>
          <span className="badge">✓ Role‑focused</span>
          <span className="badge">✓ Time‑saving</span>
        </div>
      </section>

      <div className="card" role="region" aria-label="Resume input">
        <div className="tabs" role="tablist" aria-label="Input mode">
          <button
            type="button"
            role="tab"
            className="tab"
            aria-selected={mode === 'upload'}
            onClick={() => onTab('upload')}
            disabled={loading}
          >
            Upload PDF
          </button>
          <button
            type="button"
            role="tab"
            className="tab"
            aria-selected={mode === 'paste'}
            onClick={() => onTab('paste')}
            disabled={loading}
          >
            Paste Text
          </button>
        </div>

        <div className="card-body">
          <form onSubmit={onSubmit}>
            {mode === 'upload' ? (
              <div className="field" style={{ marginBottom: 16 }}>
                <label htmlFor="resume" className="label">Resume (PDF)</label>
                <input
                  id="resume"
                  type="file"
                  accept="application/pdf"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  style={{ display: 'none' }}
                  disabled={loading}
                />
                <label
                  htmlFor="resume"
                  className="dropzone"
                  tabIndex={0}
                  onDragOver={(e) => { e.preventDefault(); e.stopPropagation() }}
                  onDrop={onDropResume}
                >
                  {file ? (
                    <span><strong>{file.name}</strong> selected</span>
                  ) : (
                    <span>Drag & drop your PDF here or <strong>browse</strong></span>
                  )}
                </label>
                <div className="hint">Only PDF files are supported for uploads.</div>
              </div>
            ) : (
              <div className="field" style={{ marginBottom: 16 }}>
                <label htmlFor="resumeText" className="label">Resume Text</label>
                <textarea
                  id="resumeText"
                  className="textarea"
                  placeholder="Paste your resume content here..."
                  value={resumeText}
                  onChange={(e) => setResumeText(e.target.value)}
                  disabled={loading}
                  rows={12}
                />
                <div className="hint">Paste plain text. Remove private details you do not want to share.</div>
              </div>
            )}

            <div className="form-grid">
              <div className="field">
                <label htmlFor="jd" className="label">Job Description</label>
                <textarea
                  id="jd"
                  className="textarea"
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the job description here..."
                  rows={14}
                  disabled={loading}
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="strategy" className="label">Short Guideline</label>
                <input
                  id="strategy"
                  className="input"
                  value={strategy}
                  onChange={(e) => setStrategy(e.target.value)}
                  placeholder="e.g., concise, ATS-optimized"
                  maxLength={20}
                  disabled={loading}
                />
                <div className="hint">Optional (max 20 chars). A short tone or focus hint.</div>
              </div>
            </div>

            <div style={{ marginTop: 16, display: 'flex', gap: 12 }}>
              <button type="submit" disabled={loading} className="btn">
                {loading ? 'Adapting…' : 'Adapt CV'}
              </button>
            </div>
          </form>

          {error && (
            <div className="error"><strong>Error:</strong> {error}</div>
          )}

          {result && (
            <div className="result">
              <div className="result-toolbar">
                <div className="seg-group" role="tablist" aria-label="Result view">
                  <button type="button" className={`seg ${view === 'formatted' ? 'seg-active' : ''}`} onClick={() => setView('formatted')}>Formatted</button>
                  <button type="button" className={`seg ${view === 'plain' ? 'seg-active' : ''}`} onClick={() => setView('plain')}>Plain</button>
                </div>
                <div className="result-actions">
                  <button type="button" className="btn-secondary" onClick={onCopy}>{copied ? 'Copied' : 'Copy'}</button>
                  <button type="button" className="btn-secondary" onClick={onDownload}>Download</button>
                  <button type="button" className="btn-secondary" onClick={onClear}>Clear</button>
                </div>
              </div>

              {view === 'formatted' ? (
                <div className="result-card">
                  {sections.map((section, si) => (
                    <div key={si}>
                      {section.blocks.map((b, bi) => {
                        switch (b.type) {
                          case 'heading':
                            return <h3 key={bi}>{renderInlineEmphasis(b.text || '')}</h3>
                          case 'subheading':
                            return <div key={bi} className="result-subtitle"><em>{renderInlineEmphasis(b.text || '')}</em></div>
                          case 'meta':
                            return <div key={bi} className="result-meta">{renderInlineEmphasis(b.text || '')}</div>
                          case 'paragraph':
                            return <p key={bi}>{renderInlineEmphasis(b.text || '')}</p>
                          case 'list':
                            return (
                              <ul key={bi}>
                                {b.items?.map((it, idx) => <li key={idx}>{renderInlineEmphasis(it)}</li>)}
                              </ul>
                            )
                          default:
                            return null
                        }
                      })}
                    </div>
                  ))}
                </div>
              ) : (
                <textarea
                  ref={plainRef}
                  className="textarea result-edit"
                  value={result}
                  onChange={(e) => { setResult(e.target.value); requestAnimationFrame(autosizePlain) }}
                  rows={1}
                />
              )}
            </div>
          )}
        </div>
      </div>

      <div className="footer">No files are stored. Results are generated on-the-fly.</div>
    </div>
  )
} 