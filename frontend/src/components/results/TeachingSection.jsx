import { GraduationCap, BookOpen, Puzzle, MessageCircle, Zap, Wrench } from 'lucide-react'

// ── New format: 'lecture_note' entities generated from main_ideas ─────────────

function LectureNotesView({ notes }) {
  return (
    <div className="space-y-6">
      <p className="text-slate-600 text-xs -mt-2">
        Lecture notes elaboradas a partir de las ideas principales del libro
      </p>
      {notes.map((note, i) => {
        const attrs    = note.attributes || {}
        const title    = attrs.title    || `Lección ${i + 1}`
        const subtitle = attrs.subtitle || ''
        const aha      = attrs.aha_moment || ''
        const keyPoint = note.extraction_text || ''
        const example  = attrs.example || ''

        return (
          <div
            key={i}
            className="bg-gradient-to-br from-green-950/20 to-slate-900 border border-green-900/50 rounded-2xl p-5 space-y-4"
          >
            {/* Header */}
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 bg-green-900/60 border border-green-800 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                <span className="text-green-400 text-xs font-bold">{i + 1}</span>
              </div>
              <div>
                <h4 className="text-white font-bold text-base leading-snug">{title}</h4>
                {subtitle && (
                  <p className="text-green-400/70 text-xs mt-0.5 font-medium">{subtitle}</p>
                )}
              </div>
            </div>

            {/* Key author point */}
            {keyPoint && (
              <div className="pl-11">
                <p className="text-slate-300 text-sm italic leading-relaxed border-l-2 border-green-800 pl-3">
                  "{keyPoint}"
                </p>
              </div>
            )}

            {/* Aha! moment */}
            {aha && (
              <div className="pl-11">
                <div className="flex items-start gap-2 bg-yellow-950/30 border border-yellow-900/40 rounded-xl px-3 py-2.5">
                  <Zap size={14} className="text-yellow-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-yellow-400 text-xs font-semibold mb-0.5">Momento Aha!</p>
                    <p className="text-yellow-200/80 text-sm leading-snug">{aha}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Example / Framework */}
            {example && (
              <div className="pl-11">
                <div className="flex items-start gap-2">
                  <Wrench size={13} className="text-slate-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-slate-500 text-xs font-medium mb-0.5">Ejemplo / Framework</p>
                    <p className="text-slate-400 text-sm leading-snug">{example}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

// ── Legacy format: 'concept/definition/example/discussion_question' ───────────

const DifficultyBadge = ({ level }) => {
  const styles = {
    basic:        'bg-green-950 text-green-400 border-green-800',
    intermediate: 'bg-yellow-950 text-yellow-400 border-yellow-800',
    advanced:     'bg-red-950 text-red-400 border-red-800',
  }
  return (
    <span className={`badge border text-xs ${styles[level] || 'bg-slate-800 text-slate-400 border-slate-700'}`}>
      {level || 'general'}
    </span>
  )
}

function LegacyView({ data }) {
  const concepts   = data.filter(e => e.extraction_class === 'concept')
  const defs       = data.filter(e => e.extraction_class === 'definition')
  const examples   = data.filter(e => e.extraction_class === 'example')
  const questions  = data.filter(e => e.extraction_class === 'discussion_question')

  return (
    <div className="space-y-8">
      {concepts.length > 0 && (
        <div>
          <h3 className="section-title text-green-400">
            <BookOpen size={18} /> Conceptos Clave
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-slate-500 border-b border-slate-800">
                  <th className="pb-2 pr-4 font-medium">Concepto</th>
                  <th className="pb-2 pr-4 font-medium">Explicación</th>
                  <th className="pb-2 font-medium">Nivel</th>
                </tr>
              </thead>
              <tbody>
                {concepts.map((c, i) => (
                  <tr key={i} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 pr-4 text-green-300 font-medium align-top">
                      {c.extraction_text.slice(0, 80)}{c.extraction_text.length > 80 ? '…' : ''}
                    </td>
                    <td className="py-3 pr-4 text-slate-400 align-top">
                      {c.attributes?.explanation || '—'}
                    </td>
                    <td className="py-3 align-top">
                      <DifficultyBadge level={c.attributes?.difficulty} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {defs.length > 0 && (
        <div>
          <h3 className="section-title text-green-400">
            <Puzzle size={18} /> Definiciones
          </h3>
          <div className="grid sm:grid-cols-2 gap-3">
            {defs.map((d, i) => (
              <div key={i} className="extraction-card border-green-900">
                <p className="text-green-300 font-bold text-sm mb-1">
                  {d.attributes?.term || 'Término'}
                </p>
                <p className="quote-text border-l-green-600 mb-2">"{d.extraction_text}"</p>
                {d.attributes?.explanation && (
                  <p className="text-slate-500 text-xs">{d.attributes.explanation}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {examples.length > 0 && (
        <div>
          <h3 className="section-title text-green-400">
            <GraduationCap size={18} /> Ejemplos Ilustrativos
          </h3>
          <div className="space-y-3">
            {examples.map((ex, i) => (
              <div key={i} className="extraction-card border-green-900">
                <p className="quote-text border-l-green-500 mb-2">"{ex.extraction_text}"</p>
                {ex.attributes?.illustrates && (
                  <p className="text-slate-500 text-xs">
                    → Ilustra: <span className="text-green-500">{ex.attributes.illustrates}</span>
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {questions.length > 0 && (
        <div>
          <h3 className="section-title text-green-400">
            <MessageCircle size={18} /> Preguntas de Discusión
          </h3>
          <div className="space-y-4">
            {questions.map((q, i) => {
              const question = q.attributes?.suggested_question || q.extraction_text
              return (
                <div key={i} className="bg-green-950/20 border border-green-900/50 rounded-xl p-5">
                  <p className="text-white font-semibold text-base mb-3">
                    {i + 1}. {question}
                  </p>
                  <div className="flex flex-wrap gap-3 text-xs">
                    {q.attributes?.learning_outcome && (
                      <span className="text-green-400">
                        🎯 {q.attributes.learning_outcome}
                      </span>
                    )}
                    {q.attributes?.difficulty && (
                      <DifficultyBadge level={q.attributes.difficulty} />
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────────

export default function TeachingSection({ data }) {
  if (data.length === 0) return <Empty />

  // New format: lecture_note entities generated by Gemini from ideas
  const lectureNotes = data.filter(e => e.extraction_class === 'lecture_note')
  if (lectureNotes.length > 0) {
    return <LectureNotesView notes={lectureNotes} />
  }

  // Legacy format: concept/definition/example/discussion_question
  return <LegacyView data={data} />
}

function Empty() {
  return (
    <div className="text-center py-12 text-slate-600">
      <GraduationCap size={32} className="mx-auto mb-2" />
      <p>No se encontraron lecture notes en este módulo.</p>
    </div>
  )
}
