import { Bot, Pin, Brain, HelpCircle, AlertTriangle } from 'lucide-react'

export default function KnowledgeBaseSection({ data }) {
  const facts        = data.filter(e => e.extraction_class === 'fact')
  const explanations = data.filter(e => e.extraction_class === 'concept_explanation')
  const qaPairs      = data.filter(e => e.extraction_class === 'qa_pair')

  if (data.length === 0) return <Empty />

  return (
    <div className="space-y-8">
      {/* Facts */}
      {facts.length > 0 && (
        <div>
          <h3 className="section-title text-orange-400">
            <Pin size={18} /> Hechos Verificables
          </h3>
          <div className="grid sm:grid-cols-2 gap-3">
            {facts.map((f, i) => (
              <div key={i} className="extraction-card border-orange-900 flex gap-3">
                <Pin size={14} className="text-orange-500 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-slate-200 text-sm leading-relaxed mb-2">
                    "{f.extraction_text}"
                  </p>
                  <div className="flex flex-wrap gap-2 text-xs">
                    {f.attributes?.topic && (
                      <span className="bg-slate-800 text-slate-400 px-2 py-0.5 rounded">
                        {f.attributes.topic}
                      </span>
                    )}
                    {f.attributes?.type && (
                      <span className={`badge border ${
                        f.attributes.type === 'established fact'
                          ? 'bg-green-950 text-green-400 border-green-800'
                          : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}>
                        {f.attributes.type}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Concept Explanations */}
      {explanations.length > 0 && (
        <div>
          <h3 className="section-title text-orange-400">
            <Brain size={18} /> Explicaciones de Conceptos
          </h3>
          <div className="space-y-4">
            {explanations.map((exp, i) => (
              <div key={i} className="extraction-card border-orange-900">
                <h4 className="text-orange-300 font-bold text-base mb-2">
                  {exp.attributes?.concept || 'Concepto'}
                </h4>
                <p className="quote-text border-l-orange-700 mb-3">
                  "{exp.extraction_text}"
                </p>
                {exp.attributes?.explanation && (
                  <p className="text-slate-300 text-sm mb-2">
                    <span className="text-slate-500 font-medium">Explicación: </span>
                    {exp.attributes.explanation}
                  </p>
                )}
                {exp.attributes?.related_concepts && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {exp.attributes.related_concepts.split(',').map((rel, j) => (
                      <span key={j} className="badge bg-orange-950 text-orange-500 border border-orange-900 text-xs">
                        {rel.trim()}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Q&A Pairs */}
      {qaPairs.length > 0 && (
        <div>
          <h3 className="section-title text-orange-400">
            <HelpCircle size={18} /> Preguntas y Respuestas
          </h3>
          <div className="space-y-4">
            {qaPairs.map((qa, i) => (
              <div
                key={i}
                className="bg-orange-950/20 border border-orange-900/50 rounded-xl overflow-hidden"
              >
                {/* Question */}
                <div className="flex items-start gap-3 p-4 border-b border-orange-900/40 bg-orange-950/30">
                  <div className="w-6 h-6 bg-orange-600 rounded-full flex items-center justify-center flex-shrink-0 text-white text-xs font-bold">
                    P
                  </div>
                  <p className="text-white font-semibold text-sm pt-0.5">
                    {qa.attributes?.question || qa.extraction_text}
                  </p>
                </div>

                {/* Answer */}
                <div className="flex items-start gap-3 p-4">
                  <div className="w-6 h-6 bg-slate-700 rounded-full flex items-center justify-center flex-shrink-0 text-slate-300 text-xs font-bold">
                    R
                  </div>
                  <p className="text-slate-300 text-sm leading-relaxed">
                    {qa.attributes?.answer || qa.extraction_text}
                  </p>
                </div>

                {/* Critical note */}
                {qa.attributes?.critical_note && (
                  <div className="flex items-start gap-2 px-4 pb-4 pt-0">
                    <AlertTriangle size={13} className="text-amber-500 flex-shrink-0 mt-0.5" />
                    <p className="text-amber-600 text-xs">
                      {qa.attributes.critical_note}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function Empty() {
  return (
    <div className="text-center py-12 text-slate-600">
      <Bot size={32} className="mx-auto mb-2" />
      <p>No se encontraron extracciones en este módulo.</p>
    </div>
  )
}
