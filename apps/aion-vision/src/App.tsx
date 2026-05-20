import { useCallback, useEffect, useState, useRef } from 'react';
import DashboardLayout from './components/layout/DashboardLayout';
import MetricTile from './components/dashboard/MetricTile';
import RecordCard from './components/dashboard/RecordCard';
import AutomationPulse from './components/dashboard/AutomationPulse';
import NexusGraph from './components/dashboard/NexusGraph';
import { Activity, Brain, Database, RefreshCw, ShieldCheck } from 'lucide-react';
import {
  EMPTY_DASHBOARD_DATA,
  compactNumber,
  formatDateTime,
  loadDashboardData,
} from './lib/dashboardData';
import type { DashboardData, SmlAgent } from './types/dashboard';

function App() {
  const [data, setData] = useState<DashboardData>(EMPTY_DASHBOARD_DATA);
  const [loading, setLoading] = useState(true);
  const autoRefreshRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refreshData = useCallback(async () => {
    setLoading(true);
    try {
      setData(await loadDashboardData());
    } finally {
      setLoading(false);
    }
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

  const statusLabel = loading ? 'SYNCING' : data.status.label;
  const currentRatio = data.totals.recordsTotal
    ? Math.round((data.totals.currentRecords * 100) / data.totals.recordsTotal)
    : 0;

  return (
    <DashboardLayout statusLabel={statusLabel} generatedAt={data.generatedAt}>
      <div className="space-y-12 max-w-7xl mx-auto">
        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricTile
            label="Всего записей"
            value={compactNumber(data.totals.recordsTotal)}
            trend={`${currentRatio}% current`}
            icon={<Database className="w-5 h-5" />}
          />
          <MetricTile
            label="Актуальная память"
            value={compactNumber(data.totals.currentRecords)}
            trend={`${compactNumber(data.totals.supersededRecords)} old`}
            icon={<Brain className="w-5 h-5" />}
            color="amber"
          />
          <MetricTile
            label="Агенты"
            value={compactNumber(data.totals.authorsTotal)}
            trend={`${compactNumber(data.totals.sourceFilesTotal)} files`}
            icon={<Activity className="w-5 h-5" />}
          />
          <MetricTile
            label="Источник"
            value={data.status.state === 'live' ? 'LIVE' : data.status.state.toUpperCase()}
            trend={formatDateTime(data.generatedAt)}
            icon={<ShieldCheck className="w-5 h-5" />}
            color="amber"
          />
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          <div className="lg:col-span-2 space-y-8">
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold">SML Live Feed</h2>
              <button
                type="button"
                onClick={() => void refreshData()}
                disabled={loading}
                className="inline-flex items-center gap-2 text-[10px] font-mono uppercase text-cyan-data border border-cyan-data/30 px-3 py-1 hover:bg-cyan-data/10 disabled:opacity-40 transition-colors"
              >
                <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
                Refresh
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
          </div>

          <div className="space-y-12">
            <section>
              <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold mb-6 border-b border-white/10 pb-4">
                Nexus Graph
              </h2>
              {data.nexusGraph && (
                <NexusGraph nodes={data.nexusGraph.nodes} links={data.nexusGraph.links} />
              )}
            </section>

            <section>
              <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold mb-6 border-b border-white/10 pb-4">
                System Pulse
              </h2>
              <AutomationPulse data={data.dailyActivity} />
            </section>

            <section className="bg-white/5 border border-white/10 p-6 rounded-sm space-y-6">
              <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold">Active Agents</h2>
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
              <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold">Record Types</h2>
              {data.typeCounts.map((item) => (
                <div key={item.type} className="flex items-center justify-between text-xs font-mono uppercase">
                  <span className="text-white/60">{item.type}</span>
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
