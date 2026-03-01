import { GraduationCap, BookOpen, Puzzle, MessageCircle } from 'lucide-react'

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

export default function TeachingSection({ data }) {
  const concepts   = data.filter(e => e.extraction_class === 'concept')
  const defs       = data.filter(e => e.extraction_class === 'definition')
  const examples   = data.filter(e => e.extraction_class === 'example')
  const questions  = data.filter(e => e.extraction_class === 'discussion_question')

  if (data.length === 0) return <Empty />

  return (
    <div className="space-y-8">
      {/* Concepts Table */}
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

      {/* Definitions */}
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

      {/* Examples */}
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

      {/* Discussion Questions */}
      {questions.length > 0 && (
        <div>
          <h3 className="section-title text-green-400">
            <MessageCircle size={18} /> Preguntas de Discusión
          </h3>
          <div className="space-y-4">
            {questions.map((q, i) => {
              const question = q.attributes?.suggested_question || q.extraction_text
              return (
                <div
                  key={i}
                  className="bg-green-950/20 border border-green-900/50 rounded-xl p-5"
                >
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

function Empty() {
  return (
    <div className="text-center py-12 text-slate-600">
      <GraduationCap size={32} className="mx-auto mb-2" />
      <p>No se encontraron extracciones en este módulo.</p>
    </div>
  )
}
