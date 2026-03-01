import { FileText, Loader2, Clock } from 'lucide-react'

const TASK_LABELS = {
  central_message:   '🎯 Mensaje Central',
  main_ideas:        '💡 Ideas Principales',
  social_media:      '📱 Redes Sociales',
  teaching_material: '🎓 Material de Clase',
  knowledge_base:    '🤖 Base de Conocimiento',
}

export default function ProcessingView({ jobState }) {
  const { file, progress, step, total, tasks = [] } = jobState

  const pct = step && total ? Math.round((step / total) * 100) : null

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-8">
      {/* Animated icon */}
      <div className="relative">
        <div className="w-24 h-24 rounded-full border-4 border-slate-800 flex items-center justify-center">
          <div className="absolute inset-0 rounded-full border-4 border-t-violet-500 animate-spin" />
          <FileText size={32} className="text-violet-400" />
        </div>
      </div>

      {/* Status */}
      <div className="space-y-2">
        <h2 className="text-2xl font-bold text-white">Analizando documento</h2>
        <p className="text-slate-400 font-medium text-sm truncate max-w-sm mx-auto">
          {file}
        </p>
      </div>

      {/* Progress bar */}
      {pct !== null && (
        <div className="w-full max-w-md">
          <div className="flex justify-between text-xs text-slate-500 mb-2">
            <span>Progreso</span>
            <span>{pct}%</span>
          </div>
          <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-violet-600 to-violet-400 rounded-full transition-all duration-700"
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>
      )}

      {/* Current task */}
      <div className="card px-6 py-4 max-w-md w-full">
        <div className="flex items-center gap-3">
          <Loader2 size={16} className="text-violet-400 animate-spin flex-shrink-0" />
          <p className="text-slate-300 text-sm text-left">
            {progress || 'Iniciando...'}
          </p>
        </div>
      </div>

      {/* Task list */}
      <div className="max-w-md w-full">
        <p className="text-slate-600 text-xs mb-3">Módulos seleccionados:</p>
        <div className="flex flex-wrap gap-2 justify-center">
          {tasks.map((taskId, i) => {
            const isDone = step && i < step - 1
            const isCurrent = step && i === step - 1
            return (
              <span
                key={taskId}
                className={`
                  text-xs px-3 py-1 rounded-full border font-medium
                  ${isDone    ? 'bg-green-950 border-green-700 text-green-400' : ''}
                  ${isCurrent ? 'bg-violet-950 border-violet-600 text-violet-300 animate-pulse' : ''}
                  ${!isDone && !isCurrent ? 'bg-slate-900 border-slate-700 text-slate-500' : ''}
                `}
              >
                {isDone && '✓ '}{TASK_LABELS[taskId] || taskId}
              </span>
            )
          })}
        </div>
      </div>

      {/* Disclaimer */}
      <div className="flex items-center gap-2 text-slate-600 text-xs">
        <Clock size={12} />
        <span>Esto puede tardar entre 2 y 15 minutos según el tamaño del libro</span>
      </div>
    </div>
  )
}
