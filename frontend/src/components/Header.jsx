import { BookOpen, RotateCcw } from 'lucide-react'

export default function Header({ onReset }) {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="container mx-auto px-4 max-w-5xl flex items-center justify-between h-14">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-violet-600 rounded-lg flex items-center justify-center">
            <BookOpen size={16} className="text-white" />
          </div>
          <div>
            <span className="font-bold text-white text-sm">Lector Doc</span>
            <span className="text-violet-400 font-bold text-sm"> Extractor</span>
          </div>
          <span className="hidden sm:inline ml-2 badge bg-violet-900 text-violet-300">
            Gemini AI
          </span>
        </div>

        {/* Reset button */}
        {onReset && (
          <button onClick={onReset} className="btn-secondary text-sm">
            <RotateCcw size={14} />
            <span className="hidden sm:inline">Nuevo documento</span>
          </button>
        )}
      </div>
    </header>
  )
}
