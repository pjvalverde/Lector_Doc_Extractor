import { useState, useRef } from 'react'
import {
  Upload, FileText, BookOpen, Zap, X, AlertCircle,
  Lightbulb, Share2, GraduationCap,
  FlaskConical
} from 'lucide-react'

// Three active modules (central_message and knowledge_base removed in v2)
const TASKS = [
  {
    id: 'main_ideas',
    label: 'Ideas Principales',
    desc: 'Ideas clave con momentos Aha!, estructura padre-hijo y frameworks del autor',
    icon: Lightbulb,
    color: 'yellow',
    bg: 'bg-yellow-950/60',
    border: 'border-yellow-700',
    selectedBg: 'bg-yellow-900/80',
    iconColor: 'text-yellow-400',
    badge: 'Base · Siempre activo',
  },
  {
    id: 'social_media',
    label: 'Redes Sociales',
    desc: 'Hasta 10 posts para X e Instagram generados desde las ideas del libro',
    icon: Share2,
    color: 'pink',
    bg: 'bg-pink-950/60',
    border: 'border-pink-700',
    selectedBg: 'bg-pink-900/80',
    iconColor: 'text-pink-400',
    badge: null,
  },
  {
    id: 'teaching_material',
    label: 'Material de Clase',
    desc: 'Lecture notes con título, subtítulo, momento Aha! y puntos clave del autor',
    icon: GraduationCap,
    color: 'green',
    bg: 'bg-green-950/60',
    border: 'border-green-700',
    selectedBg: 'bg-green-900/80',
    iconColor: 'text-green-400',
    badge: null,
  },
]

export default function UploadZone({ onSubmit, error, onClearError }) {
  const [file, setFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  // main_ideas always selected and always required
  const [selectedTasks, setSelectedTasks] = useState(TASKS.map(t => t.id))
  const [scientificMode, setScientificMode] = useState(false)
  const [loading, setLoading] = useState(false)
  const inputRef = useRef(null)

  const isPdf = file?.name?.toLowerCase().endsWith('.pdf')

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) setFile(dropped)
  }

  const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true) }
  const handleDragLeave  = () => setIsDragging(false)

  const handleFileInput = (e) => {
    const selected = e.target.files[0]
    if (selected) setFile(selected)
  }

  const toggleTask = (taskId) => {
    // main_ideas cannot be deselected — it always runs and feeds the other modules
    if (taskId === 'main_ideas') return
    setSelectedTasks(prev =>
      prev.includes(taskId)
        ? prev.filter(t => t !== taskId)
        : [...prev, taskId]
    )
  }

  const handleSubmit = async () => {
    if (!file || selectedTasks.length === 0 || loading) return
    setLoading(true)
    onClearError?.()
    try {
      await onSubmit(file, selectedTasks, scientificMode)
    } finally {
      setLoading(false)
    }
  }

  const fileIcon = file?.name.endsWith('.pdf') ? FileText
    : file?.name.endsWith('.epub') ? BookOpen
    : FileText

  const FileIcon = fileIcon

  return (
    <div className="space-y-6">
      {/* Hero */}
      <div className="text-center pt-4 pb-2">
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white mb-2">
          Extrae el conocimiento de tus{' '}
          <span className="text-violet-400">documentos</span>
        </h1>
        <p className="text-slate-400 max-w-xl mx-auto text-sm sm:text-base">
          Sube un PDF, EPUB o TXT. Gemini AI extrae las ideas principales con
          momentos <span className="text-yellow-400 font-semibold">Aha!</span> y
          genera posts y lecture notes desde ellas.
        </p>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="flex items-start gap-3 bg-red-950 border border-red-800 rounded-xl p-4 text-red-300">
          <AlertCircle size={18} className="mt-0.5 flex-shrink-0" />
          <p className="text-sm flex-1">{error}</p>
          <button onClick={onClearError}>
            <X size={16} />
          </button>
        </div>
      )}

      {/* Drop Zone */}
      <div
        onClick={() => !file && inputRef.current.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
          card p-8 text-center cursor-pointer transition-all duration-200
          ${isDragging ? 'border-violet-500 bg-violet-950/30' : 'hover:border-slate-600 hover:bg-slate-900/80'}
          ${file ? 'cursor-default' : ''}
        `}
      >
        {!file ? (
          <>
            <div className="w-14 h-14 bg-slate-800 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Upload size={24} className="text-violet-400" />
            </div>
            <p className="text-white font-semibold mb-1">
              {isDragging ? 'Suelta el archivo aquí' : 'Arrastra tu documento aquí'}
            </p>
            <p className="text-slate-500 text-sm mb-4">o haz clic para seleccionar</p>
            <div className="flex items-center justify-center gap-3 text-xs text-slate-600">
              <span className="px-2 py-1 bg-slate-800 rounded">PDF</span>
              <span className="px-2 py-1 bg-slate-800 rounded">EPUB</span>
              <span className="px-2 py-1 bg-slate-800 rounded">TXT</span>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-violet-900 rounded-xl flex items-center justify-center flex-shrink-0">
                <FileIcon size={20} className="text-violet-300" />
              </div>
              <div className="text-left">
                <p className="font-semibold text-white text-sm truncate max-w-xs">{file.name}</p>
                <p className="text-slate-500 text-xs mt-0.5">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); setFile(null) }}
              className="text-slate-500 hover:text-red-400 transition-colors p-1"
            >
              <X size={18} />
            </button>
          </div>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.epub,.txt"
        className="hidden"
        onChange={handleFileInput}
      />

      {/* Task Selection */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-white font-semibold text-sm">
            ¿Qué quieres generar?
          </h2>
          <div className="flex gap-2 text-xs">
            <button
              onClick={() => setSelectedTasks(TASKS.map(t => t.id))}
              className="text-violet-400 hover:text-violet-300"
            >
              Todas
            </button>
            <span className="text-slate-700">|</span>
            <button
              onClick={() => setSelectedTasks(['main_ideas'])}
              className="text-slate-500 hover:text-slate-400"
            >
              Solo ideas
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {TASKS.map((task) => {
            const Icon     = task.icon
            const selected = selectedTasks.includes(task.id)
            const locked   = task.id === 'main_ideas'
            return (
              <button
                key={task.id}
                onClick={() => toggleTask(task.id)}
                className={`
                  text-left p-4 rounded-xl border transition-all duration-150
                  ${selected
                    ? `${task.selectedBg} ${task.border} ring-1 ring-inset ring-opacity-50`
                    : 'bg-slate-900 border-slate-800 hover:border-slate-600'
                  }
                  ${locked ? 'cursor-default' : ''}
                `}
              >
                <div className="flex items-start gap-3">
                  <div className={`
                    w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5
                    ${selected ? task.bg : 'bg-slate-800'}
                  `}>
                    <Icon size={16} className={selected ? task.iconColor : 'text-slate-500'} />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className={`font-semibold text-sm ${selected ? 'text-white' : 'text-slate-400'}`}>
                        {task.label}
                      </p>
                      {task.badge && (
                        <span className={`text-xs px-1.5 py-0.5 rounded-full ${task.border} ${task.bg} ${task.iconColor}`}>
                          {task.badge}
                        </span>
                      )}
                    </div>
                    <p className={`text-xs mt-0.5 leading-snug ${selected ? 'text-slate-400' : 'text-slate-600'}`}>
                      {task.desc}
                    </p>
                  </div>
                </div>
                {/* Checkbox indicator */}
                <div className="flex justify-end mt-2">
                  <div className={`
                    w-4 h-4 rounded border flex items-center justify-center transition-all
                    ${selected ? `${task.border} ${task.selectedBg}` : 'border-slate-700'}
                  `}>
                    {selected && (
                      <svg viewBox="0 0 10 10" className={`w-2.5 h-2.5 ${task.iconColor}`}>
                        <path d="M1 5l3 3 5-5" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" />
                      </svg>
                    )}
                  </div>
                </div>
              </button>
            )
          })}
        </div>

        {/* How it works note */}
        <p className="text-slate-600 text-xs mt-3 flex items-center gap-1.5">
          <Lightbulb size={11} className="text-yellow-600" />
          Ideas Principales siempre se extrae primero (LangExtract + Gemini).
          Las otras secciones se generan <span className="text-slate-500">desde las ideas</span>, sin re-leer el libro.
        </p>
      </div>

      {/* Scientific Mode Toggle */}
      <div className={`
        card p-4 transition-all duration-200
        ${scientificMode ? 'border-emerald-700 bg-emerald-950/30' : ''}
      `}>
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className={`
              w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0
              ${scientificMode ? 'bg-emerald-900' : 'bg-slate-800'}
            `}>
              <FlaskConical size={18} className={scientificMode ? 'text-emerald-400' : 'text-slate-500'} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <p className={`font-semibold text-sm ${scientificMode ? 'text-emerald-300' : 'text-slate-400'}`}>
                  Modo Científico
                </p>
                {scientificMode && (
                  <span className="badge bg-emerald-900 text-emerald-400 border border-emerald-700 text-xs">
                    ACTIVO
                  </span>
                )}
              </div>
              <p className="text-slate-500 text-xs mt-0.5">
                {scientificMode
                  ? 'Gemini Vision lee cada página como imagen → fórmulas, matrices y gráficas en LaTeX ✓'
                  : 'Para libros de física, matemáticas, game theory o cualquier PDF con fórmulas'}
              </p>
              {scientificMode && !isPdf && file && (
                <p className="text-amber-500 text-xs mt-1 flex items-center gap-1">
                  <AlertCircle size={11} /> Solo funciona con PDF. Cambia el archivo o desactiva este modo.
                </p>
              )}
              {scientificMode && (
                <div className="flex flex-wrap gap-3 mt-2 text-xs text-slate-500">
                  <span className="flex items-center gap-1">
                    <span className="text-emerald-500">✓</span> Fórmulas LaTeX
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="text-emerald-500">✓</span> Matrices
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="text-emerald-500">✓</span> Gráficas descritas
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="text-amber-500">~</span> Más lento
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="text-amber-500">~</span> +$0.50 aprox.
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Toggle switch */}
          <button
            onClick={() => setScientificMode(v => !v)}
            className={`
              relative inline-flex h-6 w-11 items-center rounded-full
              transition-colors duration-200 flex-shrink-0
              ${scientificMode ? 'bg-emerald-600' : 'bg-slate-700'}
            `}
          >
            <span className={`
              inline-block h-4 w-4 transform rounded-full bg-white shadow
              transition-transform duration-200
              ${scientificMode ? 'translate-x-6' : 'translate-x-1'}
            `} />
          </button>
        </div>
      </div>

      {/* Submit Button */}
      <button
        onClick={handleSubmit}
        disabled={!file || selectedTasks.length === 0 || loading}
        className="btn-primary w-full text-base py-4"
      >
        <Zap size={18} />
        {loading ? 'Iniciando extracción...' : `Extraer con Gemini AI · ${selectedTasks.length} módulo${selectedTasks.length !== 1 ? 's' : ''}`}
      </button>

      {/* Info */}
      <p className="text-center text-slate-600 text-xs">
        El proceso puede tardar varios minutos según el tamaño del documento.
        No cierres la ventana.
      </p>
    </div>
  )
}
