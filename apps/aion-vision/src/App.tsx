import { useCallback, useEffect, useState, useRef } from 'react';
import DashboardLayout from './components/layout/DashboardLayout';
import type { DashboardView } from './components/layout/DashboardLayout';
import MetricTile from './components/dashboard/MetricTile';
import RecordCard from './components/dashboard/RecordCard';
import AutomationPulse from './components/dashboard/AutomationPulse';
import NexusGraph from './components/dashboard/NexusGraph';
import MemorySearch from './components/dashboard/MemorySearch';
import SystemHealth from './components/dashboard/SystemHealth';
import MemoryAnalytics from './components/dashboard/MemoryAnalytics';
import DriftWorkflowDashboard from './components/dashboard/DriftWorkflowDashboard';
import HhBoosterValidation from './components/dashboard/HhBoosterValidation';
import HhBoosterLanding from './components/dashboard/HhBoosterLanding';
import { Activity, Brain, Database, RefreshCw, ShieldCheck } from 'lucide-react';
import {
  EMPTY_DASHBOARD_DATA,
  compactNumber,
  formatDateTime,
  loadDashboardData,
  translateType,
} from './lib/dashboardData';
import type { DashboardData, SmlAgent } from './types/dashboard';


const viewFromHash = (): DashboardView => {
  if (typeof window === 'undefined') return 'drift';
  const hash = window.location.hash.replace('#', '').split('?')[0];
  if (hash === 'overview' || hash === 'hh-booster' || hash === 'hh-booster-public') return hash;
  return 'drift';
};

function App() {
  const [data, setData] = useState<DashboardData>(EMPTY_DASHBOARD_DATA);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState<DashboardView>(() => viewFromHash());
  const autoRefreshRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const changeView = useCallback((view: DashboardView) => {
    setActiveView(view);
    if (typeof window !== 'undefined') {
      window.location.hash = view;
    }
  }, []);

  const refreshData = useCallback(async () => {
    setLoading(true);
    try {
      setData(await loadDashboardData());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const handleHashChange = () => setActiveView(viewFromHash());
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  useEffect(() => {
    let active = true;
    
    const load = async () => {
      const nextData = await loadDashboardData();
      if (active) {
        setData(nextData);
        setLoading(false);
      }
    };

    void load();

    // Real-time Feed: автообновление каждые 30 секунд
    autoRefreshRef.current = setInterval(() => {
      void loadDashboardData().then((nextData) => {
        if (active) setData(nextData);
      });
    }, 30000);

    return () => {
      active = false;
      if (autoRefreshRef.current) clearInterval(autoRefreshRef.current);
    };
  }, []);

  const statusLabel = loading ? 'СИНХРОНИЗАЦИЯ' : data.status.label;
  const currentRatio = data.totals.recordsTotal
    ? Math.round((data.totals.currentRecords * 100) / data.totals.recordsTotal)
    : 0;

  const stateTranslation: Record<string, string> = {
    'live': 'В ЭФИРЕ',
    'empty': 'ПУСТО',
    'error': 'ОШИБКА',
  };
  const sourceValue = stateTranslation[data.status.state] || data.status.state.toUpperCase();

  const layoutStatusLabel = activeView === 'hh-booster' ? 'HH BOOSTER TEST' : statusLabel;

  if (activeView === 'drift') {
    return <DriftWorkflowDashboard onOpenOverview={() => changeView('overview')} />;
  }

  if (activeView === 'hh-booster') {
    return (
      <DashboardLayout
        statusLabel={layoutStatusLabel}
        generatedAt={data.generatedAt}
        activeView={activeView}
        onViewChange={changeView}
      >
        <HhBoosterValidation />
      </DashboardLayout>
    );
  }

  if (activeView === 'hh-booster-public') {
    return <HhBoosterLanding />;
  }

  return (
    <DashboardLayout
      statusLabel={layoutStatusLabel}
      generatedAt={data.generatedAt}
      activeView={activeView}
      onViewChange={changeView}
    >
      <div className="space-y-12 max-w-7xl mx-auto">
        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricTile
            label="Всего записей"
            value={compactNumber(data.totals.recordsTotal)}
            trend={`${currentRatio}% актуальных`}
            icon={<Database className="w-5 h-5" />}
          />
          <MetricTile
            label="Актуальная память"
            value={compactNumber(data.totals.currentRecords)}
            trend={`${compactNumber(data.totals.supersededRecords)} устар.`}
            icon={<Brain className="w-5 h-5" />}
            color="amber"
          />
          <MetricTile
            label="Агенты"
            value={compactNumber(data.totals.authorsTotal)}
            trend={`${compactNumber(data.totals.sourceFilesTotal)} файлов`}
            icon={<Activity className="w-5 h-5" />}
          />
          <MetricTile
            label="Источник"
            value={sourceValue}
            trend={formatDateTime(data.generatedAt)}
            icon={<ShieldCheck className="w-5 h-5" />}
            color="amber"
          />
        </section>


        <section className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          <div className="lg:col-span-2 space-y-8">
            <MemorySearch />

            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold">Лента SML в реальном времени</h2>
              <button
                type="button"
                onClick={() => void refreshData()}
                disabled={loading}
                className="inline-flex items-center gap-2 text-[10px] font-mono uppercase text-cyan-data border border-cyan-data/30 px-3 py-1 hover:bg-cyan-data/10 disabled:opacity-40 transition-colors"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
                Обновить
              </button>
            </div>

            <div className="space-y-6">
              {data.records.length ? (
                data.records.map((record, idx) => (
                  <RecordCard
                    key={record.id}
                    {...record}
                    id={record.id.slice(-6)}
                    delay={idx * 0.08}
                  />
                ))
              ) : (
                <div className="bg-white/5 border border-white/10 p-6 rounded-sm text-sm font-mono text-white/50">
                  {data.status.message}
                </div>
              )}
            </div>

            <MemoryAnalytics
              weekly={data.weeklyActivity}
              agents={data.agents}
              typeCounts={data.typeCounts}
            />
          </div>

          <div className="space-y-12">
            <SystemHealth health={data.health} />

            <section>
              <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold mb-6 border-b border-white/10 pb-4">
                Граф связей
              </h2>
              {data.nexusGraph && (
                <NexusGraph nodes={data.nexusGraph.nodes} links={data.nexusGraph.links} />
              )}
            </section>

            <section>
              <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold mb-6 border-b border-white/10 pb-4">
                Пульс системы
              </h2>
              <AutomationPulse data={data.dailyActivity} />
            </section>

            <section className="bg-white/5 border border-white/10 p-6 rounded-sm space-y-6">
              <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold">Активные агенты</h2>
              <div className="space-y-4">
                {data.agents.map((agent, idx) => (
                  <AgentStatus
                    key={agent.name}
                    agent={agent}
                    color={idx % 2 === 0 ? 'cyan' : 'amber'}
                  />
                ))}
              </div>
            </section>

            <section className="bg-white/5 border border-white/10 p-6 rounded-sm space-y-4">
              <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold">Типы записей</h2>
              {data.typeCounts.map((item) => (
                <div key={item.type} className="flex items-center justify-between text-xs font-mono uppercase">
                  <span className="text-white/60">{translateType(item.type)}</span>
                  <span className="text-cyan-data">{item.current}/{item.total}</span>
                </div>
              ))}
            </section>

          </div>
        </section>
      </div>
    </DashboardLayout>
  );
}

const AgentStatus = ({
  agent,
  color,
}: {
  agent: SmlAgent;
  color: 'amber' | 'cyan';
}) => (
  <div className="flex items-center justify-between group cursor-help">
    <div className="flex items-center gap-3">
      <div className={`w-1.5 h-1.5 rounded-full ${color === 'amber' ? 'bg-amber-industrial' : 'bg-cyan-data'}`}></div>
      <div>
        <span className="block text-xs font-mono uppercase tracking-wider">{agent.name}</span>
        <span className="block text-[9px] font-mono uppercase text-white/30">{formatDateTime(agent.lastUpdated)}</span>
      </div>
    </div>
    <span className="text-[10px] font-mono uppercase opacity-30 group-hover:opacity-100 transition-opacity">
      {agent.status} · {agent.records}
    </span>
  </div>
);

export default App;
