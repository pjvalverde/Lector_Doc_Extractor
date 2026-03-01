import { Lightbulb, TrendingUp, CheckSquare } from 'lucide-react'

const ImportanceDot = ({ level }) => {
  const colors = {
    high:   'bg-red-500',
    medium: 'bg-yellow-500',
    low:    'bg-green-500',
  }
  return (
    <span className={`w-2 h-2 rounded-full flex-shrink-0 mt-1.5 ${colors[level] || 'bg-slate-500'}`} />
  )
}

export default function MainIdeasSection({ data }) {
  const ideas       = data.filter(e => e.extraction_class === 'main_idea')
  const arguments_  = data.filter(e => e.extraction_class === 'argument')
  const conclusions = data.filter(e => e.extraction_class === 'conclusion')

  if (data.length === 0) return <Empty />

  return (
    <div className="space-y-6">
      {/* Main Ideas */}
      {ideas.length > 0 && (
        <div>
          <h3 className="section-title text-yellow-400">
            <Lightbulb size={18} /> Ideas Clave
            <span className="ml-auto text-xs text-slate-600 font-normal">
              🔴 alta  🟡 media  🟢 baja
            </span>
          </h3>
          <div className="space-y-3">
            {ideas.map((idea, i) => (
              <div key={i} className="extraction-card border-yellow-900 flex gap-3">
                <ImportanceDot level={idea.attributes?.importance} />
                <div>
                  <p className="text-slate-200 text-sm font-medium leading-relaxed mb-1">
                    "{idea.extraction_text}"
                  </p>
                  {idea.attributes?.summary && (
                    <p className="text-slate-500 text-xs">{idea.attributes.summary}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Arguments */}
      {arguments_.length > 0 && (
        <div>
          <h3 className="section-title text-yellow-400">
            <TrendingUp size={18} /> Argumentos
          </h3>
          <div className="space-y-3">
            {arguments_.map((arg, i) => (
              <div key={i} className="extraction-card border-yellow-900">
                <p className="quote-text border-l-yellow-600 mb-2">"{arg.extraction_text}"</p>
                {arg.attributes?.summary && (
                  <p className="text-slate-500 text-xs">{arg.attributes.summary}</p>
                )}
                {arg.attributes?.supports && (
                  <p className="text-slate-600 text-xs mt-1">
                    → Apoya: {arg.attributes.supports}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Conclusions */}
      {conclusions.length > 0 && (
        <div>
          <h3 className="section-title text-yellow-400">
            <CheckSquare size={18} /> Conclusiones
          </h3>
          <div className="space-y-3">
            {conclusions.map((con, i) => (
              <div
                key={i}
                className="bg-yellow-950/30 border border-yellow-900/60 rounded-xl p-4"
              >
                <p className="text-yellow-200 text-sm italic leading-relaxed">
                  "{con.extraction_text}"
                </p>
                {con.attributes?.summary && (
                  <p className="text-yellow-600 text-xs mt-2">— {con.attributes.summary}</p>
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
      <Lightbulb size={32} className="mx-auto mb-2" />
      <p>No se encontraron extracciones en este módulo.</p>
    </div>
  )
}
