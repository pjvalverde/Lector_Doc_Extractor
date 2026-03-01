import { useState } from 'react'
import { Share2, Twitter, Instagram, Flame, Copy, Check } from 'lucide-react'

function CopyButton({ text }) {
  const [copied, setCopied] = useState(false)
  const copy = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }
  return (
    <button
      onClick={copy}
      className="text-slate-500 hover:text-slate-300 transition-colors p-1"
      title="Copiar"
    >
      {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
    </button>
  )
}

export default function SocialMediaSection({ data }) {
  const quotes   = data.filter(e => e.extraction_class === 'quote')
  const insights = data.filter(e => e.extraction_class === 'insight')
  const hooks    = data.filter(e => e.extraction_class === 'hook')

  if (data.length === 0) return <Empty />

  return (
    <div className="space-y-8">
      {/* Twitter Posts */}
      {quotes.length > 0 && (
        <div>
          <h3 className="section-title text-pink-400">
            <Twitter size={18} /> Posts para X (Twitter)
          </h3>
          <div className="grid sm:grid-cols-2 gap-4">
            {quotes.map((q, i) => {
              const tweet = q.attributes?.tweet || q.extraction_text
              return (
                <div key={i} className="extraction-card border-pink-900 flex flex-col gap-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <div className="w-7 h-7 bg-black rounded-full flex items-center justify-center flex-shrink-0">
                        <Twitter size={12} className="text-white" />
                      </div>
                      <span className="text-slate-500 text-xs">Post {i + 1}</span>
                    </div>
                    <CopyButton text={tweet} />
                  </div>
                  <p className="text-white text-sm leading-relaxed whitespace-pre-line">{tweet}</p>
                  <div className="flex items-center justify-between text-xs text-slate-600 border-t border-slate-700 pt-2">
                    <span>{tweet.length}/280 chars</span>
                    {q.attributes?.virality && (
                      <span className="flex items-center gap-1">
                        <Flame size={11} className={q.attributes.virality === 'high' ? 'text-orange-400' : 'text-slate-500'} />
                        viralidad {q.attributes.virality}
                      </span>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Instagram Posts */}
      {quotes.filter(q => q.attributes?.instagram_caption).length > 0 && (
        <div>
          <h3 className="section-title text-pink-400">
            <Instagram size={18} /> Captions para Instagram
          </h3>
          <div className="grid sm:grid-cols-2 gap-4">
            {quotes
              .filter(q => q.attributes?.instagram_caption)
              .map((q, i) => {
                const caption = q.attributes.instagram_caption
                return (
                  <div key={i} className="extraction-card border-pink-900">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 bg-gradient-to-br from-purple-600 to-pink-500 rounded-full flex items-center justify-center">
                          <Instagram size={12} className="text-white" />
                        </div>
                        <span className="text-slate-500 text-xs">Post {i + 1}</span>
                      </div>
                      <CopyButton text={caption} />
                    </div>
                    <p className="text-slate-200 text-sm leading-relaxed whitespace-pre-line">
                      {caption}
                    </p>
                  </div>
                )
              })}
          </div>
        </div>
      )}

      {/* Insights */}
      {insights.length > 0 && (
        <div>
          <h3 className="section-title text-pink-400">
            <Flame size={18} /> Insights Clave
          </h3>
          <div className="space-y-3">
            {insights.map((ins, i) => (
              <div key={i} className="extraction-card border-pink-900">
                <p className="quote-text border-l-pink-500 mb-2">"{ins.extraction_text}"</p>
                {ins.attributes?.takeaway && (
                  <p className="text-pink-300 text-sm font-medium mb-1">
                    💡 {ins.attributes.takeaway}
                  </p>
                )}
                {ins.attributes?.hashtags && (
                  <p className="text-pink-600 text-xs">{ins.attributes.hashtags}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Hooks */}
      {hooks.length > 0 && (
        <div>
          <h3 className="section-title text-pink-400">
            <Share2 size={18} /> Hooks de Atención
          </h3>
          <div className="grid sm:grid-cols-2 gap-3">
            {hooks.map((h, i) => (
              <div key={i} className="bg-gradient-to-br from-pink-950/40 to-slate-900 border border-pink-900/50 rounded-xl p-4">
                <p className="text-pink-200 font-semibold text-sm mb-2 italic">
                  "{h.extraction_text}"
                </p>
                {h.attributes?.attention_reason && (
                  <p className="text-slate-500 text-xs mb-2">{h.attributes.attention_reason}</p>
                )}
                {h.attributes?.platform && (
                  <span className="badge bg-pink-950 text-pink-400 border border-pink-800">
                    {h.attributes.platform}
                  </span>
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
      <Share2 size={32} className="mx-auto mb-2" />
      <p>No se encontraron extracciones en este módulo.</p>
    </div>
  )
}
