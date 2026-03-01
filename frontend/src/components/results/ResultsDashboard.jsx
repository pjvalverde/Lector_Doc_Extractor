import { useState } from 'react'
import { Download, RotateCcw, Target, Lightbulb, Share2, GraduationCap, Bot } from 'lucide-react'
import { getDownloadUrl } from '../../api/client'
import CentralMessageSection from './CentralMessageSection'
import MainIdeasSection from './MainIdeasSection'
import SocialMediaSection from './SocialMediaSection'
import TeachingSection from './TeachingSection'
import KnowledgeBaseSection from './KnowledgeBaseSection'

const TABS = [
  { id: 'central_message',   label: 'Mensaje Central',      Icon: Target,        color: 'blue'   },
  { id: 'main_ideas',        label: 'Ideas Principales',    Icon: Lightbulb,     color: 'yellow' },
  { id: 'social_media',      label: 'Redes Sociales',       Icon: Share2,        color: 'pink'   },
  { id: 'teaching_material', label: 'Material de Clase',    Icon: GraduationCap, color: 'green'  },
  { id: 'knowledge_base',    label: 'Base de Conocimiento', Icon: Bot,           color: 'orange' },
]

const TAB_COLORS = {
  blue:   { active: 'border-blue-500 text-blue-400',   hover: 'hover:text-blue-400' },
  yellow: { active: 'border-yellow-500 text-yellow-400', hover: 'hover:text-yellow-400' },
  pink:   { active: 'border-pink-500 text-pink-400',   hover: 'hover:text-pink-400' },
  green:  { active: 'border-green-500 text-green-400', hover: 'hover:text-green-400' },
  orange: { active: 'border-orange-500 text-orange-400', hover: 'hover:text-orange-400' },
}

export default function ResultsDashboard({ jobState, jobId, onReset }) {
  const { file, results = {}, tasks = [] } = jobState
  const availableTabs = TABS.filter(t => tasks.includes(t.id) && results[t.id]?.length > 0)
  const [activeTab, setActiveTab] = useState(availableTabs[0]?.id || TABS[0].id)

  const bookName = file?.replace(/\.[^.]+$/, '') || 'documento'

  const totalExtractions = Object.values(results).reduce((sum, arr) => sum + (arr?.length || 0), 0)

  return (
    <div className="space-y-6">
      {/* Summary header */}
      <div className="card p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-white font-bold text-lg truncate">{bookName}</h2>
          <p className="text-slate-400 text-sm mt-1">
            <span className="text-violet-400 font-semibold">{totalExtractions}</span> extracciones ·{' '}
            <span className="text-violet-400 font-semibold">{availableTabs.length}</span> módulos completados
          </p>
        </div>

        {/* Download buttons */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <a
            href={getDownloadUrl(jobId, 'markdown')}
            download
            className="btn-secondary text-sm"
          >
            <Download size={14} />
            Reporte .md
          </a>
          <a
            href={getDownloadUrl(jobId, 'json')}
            download
            className="btn-secondary text-sm"
          >
            <Download size={14} />
            JSON Bot
          </a>
          <button onClick={onReset} className="btn-secondary text-sm">
            <RotateCcw size={14} />
            <span className="hidden sm:inline">Nuevo</span>
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-800">
        <div className="flex gap-0 overflow-x-auto scrollbar-hide -mb-px">
          {availableTabs.map((tab) => {
            const colors = TAB_COLORS[tab.color]
            const isActive = activeTab === tab.id
            const count = results[tab.id]?.length || 0
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 whitespace-nowrap
                  transition-all duration-150 flex-shrink-0
                  ${isActive
                    ? `${colors.active} border-opacity-100`
                    : `border-transparent text-slate-500 ${colors.hover}`
                  }
                `}
              >
                <tab.Icon size={15} />
                <span className="hidden sm:inline">{tab.label}</span>
                <span className="sm:hidden">{tab.label.split(' ')[0]}</span>
                <span className={`
                  badge text-xs
                  ${isActive ? 'bg-slate-800 text-slate-300' : 'bg-slate-900 text-slate-600'}
                `}>
                  {count}
                </span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Tab content */}
      <div>
        {activeTab === 'central_message'   && <CentralMessageSection data={results.central_message   || []} />}
        {activeTab === 'main_ideas'        && <MainIdeasSection       data={results.main_ideas        || []} />}
        {activeTab === 'social_media'      && <SocialMediaSection     data={results.social_media      || []} />}
        {activeTab === 'teaching_material' && <TeachingSection        data={results.teaching_material || []} />}
        {activeTab === 'knowledge_base'    && <KnowledgeBaseSection   data={results.knowledge_base    || []} />}
      </div>
    </div>
  )
}
