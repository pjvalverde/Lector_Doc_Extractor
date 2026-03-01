import { Target, Star, Shield, Layers } from 'lucide-react'

const ConfidenceBadge = ({ value }) => {
  const styles = {
    certain: 'bg-green-950 text-green-400 border-green-800',
    likely:  'bg-yellow-950 text-yellow-400 border-yellow-800',
    possible:'bg-slate-800 text-slate-400 border-slate-700',
  }
  const style = styles[value] || styles.possible
  return (
    <span className={`badge border text-xs ${style}`}>
      {value || 'posible'}
    </span>
  )
}

const StrengthBadge = ({ value }) => {
  const styles = {
    strong:   'text-green-400',
    moderate: 'text-yellow-400',
    weak:     'text-red-400',
  }
  return <span className={`text-xs font-semibold ${styles[value] || 'text-slate-400'}`}>{value}</span>
}

export default function CentralMessageSection({ data }) {
  const theses   = data.filter(e => e.extraction_class === 'thesis')
  const coreMsgs = data.filter(e => e.extraction_class === 'core_message')
  const evidence = data.filter(e => e.extraction_class === 'supporting_evidence')

  if (data.length === 0) {
    return <Empty />
  }

  return (
    <div className="space-y-6">
      {/* Theses */}
      {theses.length > 0 && (
        <div>
          <h3 className="section-title text-blue-400">
            <Target size={18} /> Tesis Principal
          </h3>
          {theses.map((t, i) => (
            <div key={i} className="extraction-card border-blue-900">
              <div className="flex items-start justify-between gap-3 mb-3">
                <p className="quote-text border-l-blue-500 flex-1">
                  "{t.extraction_text}"
                </p>
                <ConfidenceBadge value={t.attributes?.confidence} />
              </div>
              {t.attributes?.summary && (
                <p className="text-slate-400 text-sm">
                  <span className="text-slate-500 font-medium">Resumen: </span>
                  {t.attributes.summary}
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Core Messages */}
      {coreMsgs.length > 0 && (
        <div>
          <h3 className="section-title text-blue-400">
            <Star size={18} /> Mensajes Clave
          </h3>
          {coreMsgs.map((cm, i) => (
            <div key={i} className="extraction-card border-blue-900">
              <p className="quote-text border-l-blue-400 mb-2">
                "{cm.extraction_text}"
              </p>
              {cm.attributes?.centrality && (
                <p className="text-slate-500 text-xs">{cm.attributes.centrality}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Supporting Evidence */}
      {evidence.length > 0 && (
        <div>
          <h3 className="section-title text-blue-400">
            <Shield size={18} /> Evidencia de Soporte
          </h3>
          <div className="space-y-3">
            {evidence.map((ev, i) => (
              <div key={i} className="extraction-card border-blue-900">
                <p className="quote-text border-l-slate-600 mb-2">
                  "{ev.extraction_text}"
                </p>
                <div className="flex items-center gap-4 text-xs text-slate-500">
                  {ev.attributes?.strength && (
                    <span>Fuerza: <StrengthBadge value={ev.attributes.strength} /></span>
                  )}
                  {ev.attributes?.type && (
                    <span className="bg-slate-800 px-2 py-0.5 rounded">{ev.attributes.type}</span>
                  )}
                </div>
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
      <Layers size={32} className="mx-auto mb-2" />
      <p>No se encontraron extracciones en este módulo.</p>
    </div>
  )
}
