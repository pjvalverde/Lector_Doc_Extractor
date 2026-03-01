import { FileText, Loader2, Clock, FlaskConical, Zap } from 'lucide-react'

const TASK_LABELS = {
  main_ideas:        '💡 Ideas Principales',
  social_media:      '📱 Redes Sociales',
  teaching_material: '🎓 Lecture Notes',
}

export default function ProcessingView({ jobState }) {
  const {
    file, progress, step, total, tasks = [],
    scientific_mode, phase, pct: transcriptPct,
  } = jobState

  const isTranscribing = phase === 'transcription'
  const isExtracting   = phase === 'extraction' || (!phase && step)

  // Progress bar value
  let barPct = null
  if (isTranscribing && transcriptPct != null) {
    // Transcription = first 50% of total work in scientific mode
    barPct = Math.round(transcriptPct / 2)
  } else if (isExtracting && step && total) {
    const base = scientific_mode ? 50 : 0
    const range = scientific_mode ? 50 : 100
    barPct = base + Math.round((step / total) * range)
  }

  const accentColor = isTranscribing ? 'emerald' : 'violet'

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-8">

      {/* Animated icon */}
      <div className="relative">
        <div className="w-24 h-24 rounded-full border-4 border-slate-800 flex items-center justify-center">
          <div className={`
            absolute inset-0 rounded-full border-4 border-t-${accentColor}-500 animate-spin
          `} />
          {isTranscribing
            ? <FlaskConical size={32} className="text-emerald-400" />
            : <FileText    size={32} className="text-violet-400" />
          }
        </div>
      </div>

      {/* Status title */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold text-white">
          {isTranscribing ? '🔬 Transcripción Científica' : 'Analizando documento'}
        </h2>
        <p className="text-slate-400 font-medium text-sm truncate max-w-sm mx-auto">{file}</p>
        {scientific_mode && (
          <span className="inline-flex items-center gap-1 badge bg-emerald-900 text-emerald-400 border border-emerald-700 text-xs">
            <FlaskConical size={11} /> Modo Científico activo
          </span>
        )}
      </div>

      {/* Phase indicator (scientific mode only) */}
      {scientific_mode && (
        <div className="flex items-center gap-3 max-w-sm w-full justify-center">
          <div className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border
            ${isTranscribing
              ? 'bg-emerald-900 border-emerald-600 text-emerald-300'
              : 'bg-green-950 border-green-700 text-green-400'
            }`}>
            {isTranscribing
              ? <Loader2 size={11} className="animate-spin" />
              : <span>✓</span>
            }
            Fase 1: Transcripción
          </div>
          <span className="text-slate-700">→</span>
          <div className={`flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-full border
            ${isExtracting && !isTranscribing
              ? 'bg-violet-900 border-violet-600 text-violet-300'
              : 'bg-slate-900 border-slate-700 text-slate-500'
            }`}>
            {isExtracting && !isTranscribing
              ? <Loader2 size={11} className="animate-spin" />
              : <Zap size={11} />
            }
            Fase 2: Extracción
          </div>
        </div>
      )}

      {/* Progress bar */}
      {barPct !== null && (
        <div className="w-full max-w-md">
          <div className="flex justify-between text-xs text-slate-500 mb-2">
            <span>{isTranscribing ? 'Transcribiendo páginas...' : 'Extrayendo conocimiento...'}</span>
            <span>{barPct}%</span>
          </div>
          <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-700
                ${isTranscribing
                  ? 'bg-gradient-to-r from-emerald-700 to-emerald-400'
                  : 'bg-gradient-to-r from-violet-600 to-violet-400'
                }`}
              style={{ width: `${barPct}%` }}
            />
          </div>
        </div>
      )}

      {/* Current status message */}
      <div className={`card px-6 py-4 max-w-md w-full border-${isTranscribing ? 'emerald' : 'slate'}-800`}>
        <div className="flex items-center gap-3">
          <Loader2
            size={16}
            className={`${isTranscribing ? 'text-emerald-400' : 'text-violet-400'} animate-spin flex-shrink-0`}
          />
          <p className="text-slate-300 text-sm text-left">
            {progress || 'Iniciando...'}
          </p>
        </div>
      </div>

      {/* Task pills (extraction phase) */}
      {tasks.length > 0 && (
        <div className="max-w-md w-full">
          <p className="text-slate-600 text-xs mb-3">Módulos de extracción:</p>
          <div className="flex flex-wrap gap-2 justify-center">
            {tasks.map((taskId, i) => {
              const isDone    = isExtracting && step && i < step - 1
              const isCurrent = isExtracting && step && i === step - 1
              const isPending = !isDone && !isCurrent
              return (
                <span
                  key={taskId}
                  className={`
                    text-xs px-3 py-1 rounded-full border font-medium transition-all
                    ${isDone    ? 'bg-green-950 border-green-700 text-green-400' : ''}
                    ${isCurrent ? 'bg-violet-950 border-violet-600 text-violet-300 animate-pulse' : ''}
                    ${isPending ? 'bg-slate-900 border-slate-700 text-slate-500' : ''}
                  `}
                >
                  {isDone && '✓ '}{TASK_LABELS[taskId] || taskId}
                </span>
              )
            })}
          </div>
        </div>
      )}

      {/* Time estimate */}
      <div className="flex items-center gap-2 text-slate-600 text-xs">
        <Clock size={12} />
        <span>
          {scientific_mode
            ? 'Modo Científico: 10–30 minutos según el tamaño del libro'
            : 'Esto puede tardar entre 2 y 15 minutos según el tamaño del libro'}
        </span>
      </div>
    </div>
  )
}
