import { useState, useEffect, useRef } from 'react'
import { createJob, getJob } from './api/client'
import Header from './components/Header'
import UploadZone from './components/UploadZone'
import ProcessingView from './components/ProcessingView'
import ResultsDashboard from './components/results/ResultsDashboard'

const POLL_INTERVAL = 3000 // ms

export default function App() {
  const [view, setView] = useState('upload')   // 'upload' | 'processing' | 'results'
  const [jobId, setJobId] = useState(null)
  const [jobState, setJobState] = useState(null)
  const [error, setError] = useState(null)
  const pollRef = useRef(null)

  // ── Poll for job status ──────────────────────────────────────────────────
  useEffect(() => {
    if (!jobId || view === 'upload') return

    const poll = async () => {
      try {
        const state = await getJob(jobId)
        setJobState(state)

        if (state.status === 'completed') {
          clearInterval(pollRef.current)
          setView('results')
        } else if (state.status === 'failed') {
          clearInterval(pollRef.current)
          setError(state.error || 'Ocurrió un error en la extracción.')
          setView('upload')
        }
      } catch (e) {
        console.error('Polling error:', e)
      }
    }

    poll() // immediate first call
    pollRef.current = setInterval(poll, POLL_INTERVAL)

    return () => clearInterval(pollRef.current)
  }, [jobId, view])

  // ── Handlers ─────────────────────────────────────────────────────────────
  const handleStartExtraction = async (file, selectedTasks, scientificMode) => {
    setError(null)
    try {
      const job = await createJob(file, selectedTasks, scientificMode)
      setJobId(job.job_id)
      setJobState({ status: 'pending', file: job.file, tasks: selectedTasks, scientific_mode: scientificMode })
      setView('processing')
    } catch (e) {
      const msg = e.response?.data?.detail || e.message || 'Error al iniciar la extracción'
      setError(msg)
    }
  }

  const handleReset = () => {
    clearInterval(pollRef.current)
    setJobId(null)
    setJobState(null)
    setError(null)
    setView('upload')
  }

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen flex flex-col">
      <Header onReset={view !== 'upload' ? handleReset : null} />

      <main className="flex-1 container mx-auto px-4 py-8 max-w-5xl">
        {view === 'upload' && (
          <UploadZone
            onSubmit={handleStartExtraction}
            error={error}
            onClearError={() => setError(null)}
          />
        )}

        {view === 'processing' && jobState && (
          <ProcessingView jobState={jobState} />
        )}

        {view === 'results' && jobState && (
          <ResultsDashboard jobState={jobState} jobId={jobId} onReset={handleReset} />
        )}
      </main>

      <footer className="text-center text-slate-600 text-xs py-4">
        Lector Doc Extractor · Powered by Gemini AI + LangExtract
      </footer>
    </div>
  )
}
