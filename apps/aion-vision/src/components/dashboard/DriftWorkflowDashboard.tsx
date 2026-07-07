import { useEffect, useMemo, useState, type CSSProperties } from 'react';
import {
  ArrowLeft,
  CheckCircle2,
  CircleDot,
  Lock,
  PauseCircle,
  ShieldCheck,
  Timer,
  Wrench,
  Zap,
} from 'lucide-react';
import { DRIFT_WORKFLOW_FALLBACK, loadDriftWorkflowSnapshot } from '../../lib/driftWorkflowData';
import type { DriftAgent, DriftWorkflowSnapshot, DriftWorkflowState } from '../../types/driftWorkflow';

type DriftWorkflowDashboardProps = {
  onOpenOverview?: () => void;
};

const stateMeta: Record<DriftWorkflowState, { label: string; short: string; icon: React.ReactNode; tone: string }> = {
  active: {
    label: 'работает',
    short: 'раб',
    icon: <Zap className="h-3.5 w-3.5" />,
    tone: 'border-red-400/55 bg-red-500/20 text-red-50',
  },
  next: {
    label: 'следующий',
    short: 'след',
    icon: <CircleDot className="h-3.5 w-3.5" />,
    tone: 'border-amber-industrial/60 bg-amber-industrial/20 text-amber-50',
  },
  waiting: {
    label: 'ожидает',
    short: 'ждет',
    icon: <PauseCircle className="h-3.5 w-3.5" />,
    tone: 'border-white/20 bg-black/35 text-white/60',
  },
  blocked: {
    label: 'блокер',
    short: 'блок',
    icon: <ShieldCheck className="h-3.5 w-3.5" />,
    tone: 'border-red-500/65 bg-red-500/20 text-red-50',
  },
  revision: {
    label: 'диагностика',
    short: 'диаг',
    icon: <Wrench className="h-3.5 w-3.5" />,
    tone: 'border-blue-400/55 bg-blue-500/20 text-blue-50',
  },
  done: {
    label: 'готово',
    short: 'готово',
    icon: <CheckCircle2 className="h-3.5 w-3.5" />,
    tone: 'border-green-400/55 bg-green-500/20 text-green-50',
  },
};

const hotspotPositions: Record<string, { x: number; y: number; anchor?: 'left' | 'right' | 'center' }> = {
  mimo: { x: 39, y: 34, anchor: 'center' },
  'antigravity-l1': { x: 32, y: 11, anchor: 'center' },
  'antigravity-l2': { x: 71, y: 11, anchor: 'center' },
  'codex-l3': { x: 50, y: 30, anchor: 'center' },
  'codex-l4': { x: 12, y: 66, anchor: 'left' },
  'claude-l5': { x: 92, y: 84, anchor: 'center' },
};

const smokePuffs = [
  { id: 'rear-1', x: 56.4, y: 39.5, width: 68, height: 44, delay: '0ms', duration: '4.2s', driftX: 19, driftY: -17, scale: 1.6, blur: 13, opacity: 0.42, rotate: 8 },
  { id: 'rear-2', x: 59.2, y: 36.8, width: 92, height: 58, delay: '580ms', duration: '5.1s', driftX: 32, driftY: -23, scale: 1.85, blur: 15, opacity: 0.34, rotate: 14 },
  { id: 'rear-3', x: 62.3, y: 38.7, width: 118, height: 72, delay: '1180ms', duration: '5.8s', driftX: 42, driftY: -28, scale: 2.05, blur: 18, opacity: 0.27, rotate: 20 },
  { id: 'rear-4', x: 58.1, y: 43.5, width: 76, height: 42, delay: '1800ms', duration: '4.7s', driftX: 25, driftY: -15, scale: 1.7, blur: 14, opacity: 0.32, rotate: 4 },
  { id: 'rear-5', x: 64.6, y: 42.5, width: 96, height: 48, delay: '2460ms', duration: '6.2s', driftX: 48, driftY: -19, scale: 1.95, blur: 20, opacity: 0.2, rotate: 25 },
];

const smokeWisps = [
  { id: 'wisp-1', x: 54.8, y: 43.2, width: 118, delay: '160ms', duration: '3.8s', driftX: 22, driftY: -9, rotate: 7 },
  { id: 'wisp-2', x: 58.4, y: 46.1, width: 152, delay: '980ms', duration: '4.6s', driftX: 36, driftY: -14, rotate: 11 },
  { id: 'wisp-3', x: 61.7, y: 41.4, width: 134, delay: '1720ms', duration: '5.2s', driftX: 42, driftY: -18, rotate: 17 },
];

const decisionLabels = {
  approve: 'принято',
  diagnose: 'диагностика',
  pending: 'ожидает',
  blocked: 'блокер',
};

const findCurrentLevelAgent = (snapshot: DriftWorkflowSnapshot) => {
  const exact = snapshot.agents.find((agent) => agent.level === snapshot.currentLevel);
  if (exact) return exact;

  if (snapshot.currentLevel === 'L1') {
    return (
      snapshot.agents.find((agent) => agent.level.startsWith('L1.') && agent.state === 'active')
      || snapshot.agents.find((agent) => agent.level.startsWith('L1.') && agent.state === 'next')
      || snapshot.agents.find((agent) => agent.level === 'L1.1')
      || snapshot.agents.find((agent) => agent.level === 'L1.0')
    );
  }

  return undefined;
};

const initialSelectedAgentId = (snapshot: DriftWorkflowSnapshot) => (
  snapshot.agents.find((agent) => agent.state === 'active')?.id
  || snapshot.agents.find((agent) => agent.state === 'next')?.id
  || findCurrentLevelAgent(snapshot)?.id
  || snapshot.agents[0]?.id
  || 'claude-l5'
);

const DriftWorkflowDashboard = ({ onOpenOverview }: DriftWorkflowDashboardProps) => {
  const [snapshot, setSnapshot] = useState<DriftWorkflowSnapshot>(DRIFT_WORKFLOW_FALLBACK);
  const [loadState, setLoadState] = useState<'loading' | 'live' | 'fallback'>('loading');
  const currentAgent = findCurrentLevelAgent(snapshot);
  const [selectedAgentId, setSelectedAgentId] = useState(() => initialSelectedAgentId(DRIFT_WORKFLOW_FALLBACK));

  useEffect(() => {
    let active = true;

    void loadDriftWorkflowSnapshot().then((nextSnapshot) => {
      if (!active) return;
      setSnapshot(nextSnapshot);
      setSelectedAgentId(initialSelectedAgentId(nextSnapshot));
      setLoadState(nextSnapshot.source ? 'live' : 'fallback');
    });

    return () => {
      active = false;
    };
  }, []);

  const selectedAgent = useMemo(
    () => snapshot.agents.find((agent) => agent.id === selectedAgentId) || snapshot.agents[0],
    [selectedAgentId, snapshot.agents],
  );
  const activeAgent = snapshot.agents.find((agent) => agent.state === 'active')
    || snapshot.agents.find((agent) => agent.state === 'next')
    || currentAgent
    || selectedAgent;
  const doneCount = snapshot.agents.filter((agent) => agent.state === 'done').length;
  const pendingCount = snapshot.agents.filter((agent) => agent.state === 'waiting' || agent.state === 'next').length;
  const currentMetricState: DriftWorkflowState = snapshot.state === 'done' ? 'done' : 'active';

  return (
    <main className="arena-product min-h-screen bg-[#030507] text-white">
      <div className="mx-auto flex min-h-screen w-full max-w-[1720px] flex-col gap-4 p-3 md:p-5">
        <header className="arena-shell-panel flex flex-col gap-4 px-4 py-3 md:flex-row md:items-center md:justify-between">
          <div>
            <div className="text-[10px] font-mono uppercase tracking-[0.34em] text-cyan-data/80">Aion Vision</div>
            <h1 className="mt-1 text-2xl font-black tracking-tight md:text-3xl">Drift Workflow Control</h1>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <MetricPill label={snapshot.state === 'done' ? 'финал' : 'сейчас'} value={`${activeAgent.level} ${activeAgent.name}`} state={currentMetricState} />
            <MetricPill label="готово" value={`${doneCount}/${snapshot.agents.length}`} state="done" />
            <MetricPill label="в очереди" value={`${pendingCount}`} state="next" />
            {onOpenOverview && (
              <button type="button" onClick={onOpenOverview} className="arena-control">
                <ArrowLeft className="h-4 w-4" />
                SML
              </button>
            )}
          </div>
        </header>

        <section className="grid min-h-0 flex-1 grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
          <div className="arena-shell-panel min-w-0 p-3">
            <ArenaStage
              agents={snapshot.agents}
              activeAgent={activeAgent}
              selectedAgent={selectedAgent}
              referenceRender={snapshot.referenceRender}
              onSelectAgent={setSelectedAgentId}
            />
          </div>

          <aside className="grid gap-4 xl:grid-rows-[auto_auto_1fr]">
            <SelectedInspector agent={selectedAgent} />
            <LimitsPanel snapshot={snapshot} />
            <DiagnosticsPanel snapshot={snapshot} loadState={loadState} />
            <EventPanel snapshot={snapshot} />
          </aside>
        </section>
      </div>
    </main>
  );
};

const MetricPill = ({
  label,
  value,
  state,
}: {
  label: string;
  value: string;
  state: DriftWorkflowState;
}) => (
  <div className={`inline-flex h-10 items-center gap-2 border px-3 font-mono text-[10px] uppercase tracking-[0.14em] ${stateMeta[state].tone}`}>
    {stateMeta[state].icon}
    <span className="text-white/45">{label}</span>
    <span>{value}</span>
  </div>
);

const ArenaStage = ({
  agents,
  activeAgent,
  selectedAgent,
  referenceRender,
  onSelectAgent,
}: {
  agents: DriftAgent[];
  activeAgent: DriftAgent;
  selectedAgent: DriftAgent;
  referenceRender: string;
  onSelectAgent: (id: string) => void;
}) => (
  <div className="arena-stage-clean relative min-h-[620px] overflow-hidden border border-white/10 bg-black">
    <div
      className="arena-crop absolute inset-0"
      style={{ backgroundImage: `url(${referenceRender})` }}
      aria-hidden="true"
    />
    <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_45%,transparent_38%,rgba(0,0,0,0.2)_72%,rgba(0,0,0,0.52)_100%)]" />
    <HandoffLine />
    <ActivePlatformPulse agent={activeAgent} />
    <SmokeLayer agent={activeAgent} />

    {agents.map((agent) => (
      <AgentHotspot
        key={agent.id}
        agent={agent}
        selected={selectedAgent.id === agent.id}
        onSelect={onSelectAgent}
      />
    ))}

    <SubagentOrbit agent={activeAgent} />
  </div>
);

const HandoffLine = () => (
  <svg className="arena-handoff-line pointer-events-none absolute inset-0 z-[3]" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
    <path
      className="arena-handoff-line-shadow"
      d="M39 34 C30 28 25 17 32 11 C44 5 61 5 71 11 C70 20 59 26 50 30 C36 39 19 52 12 66 C34 87 70 88 92 84"
    />
    <path
      className="arena-handoff-line-core"
      d="M39 34 C30 28 25 17 32 11 C44 5 61 5 71 11 C70 20 59 26 50 30 C36 39 19 52 12 66 C34 87 70 88 92 84"
    />
  </svg>
);

const ActivePlatformPulse = ({ agent }: { agent: DriftAgent }) => {
  const position = hotspotPositions[agent.id] || { x: agent.position.x, y: agent.position.y };
  return (
    <div
      className="arena-active-platform pointer-events-none absolute z-[3]"
      style={{
        left: `${position.x}%`,
        top: `${position.y}%`,
        '--active-accent': agent.accent,
      } as CSSProperties}
      aria-hidden="true"
    />
  );
};

const clampPercent = (value: number) => Math.max(4, Math.min(96, value));

const SmokeLayer = ({ agent }: { agent: DriftAgent }) => {
  const position = hotspotPositions[agent.id] || { x: agent.position.x, y: agent.position.y };
  const smokeX = (x: number) => clampPercent(position.x + ((x - 60) * 0.54));
  const smokeY = (y: number) => clampPercent(position.y + ((y - 40) * 0.46));

  return (
    <div className="pointer-events-none absolute inset-0 z-[4]" aria-hidden="true">
      {smokePuffs.map((puff) => (
        <span
          key={puff.id}
          className="arena-smoke-puff"
          style={{
            left: `${smokeX(puff.x)}%`,
            top: `${smokeY(puff.y)}%`,
            width: `${puff.width}px`,
            height: `${puff.height}px`,
            '--smoke-drift-x': `${puff.driftX}px`,
            '--smoke-drift-y': `${puff.driftY}px`,
            '--smoke-scale': puff.scale,
            '--smoke-blur': `${puff.blur}px`,
            '--smoke-opacity': puff.opacity,
            '--smoke-rotate': `${puff.rotate}deg`,
            '--smoke-duration': puff.duration,
            animationDelay: puff.delay,
          } as CSSProperties}
        />
      ))}
      {smokeWisps.map((wisp) => (
        <span
          key={wisp.id}
          className="arena-smoke-wisp"
          style={{
            left: `${smokeX(wisp.x)}%`,
            top: `${smokeY(wisp.y)}%`,
            width: `${wisp.width}px`,
            '--wisp-drift-x': `${wisp.driftX}px`,
            '--wisp-drift-y': `${wisp.driftY}px`,
            '--wisp-rotate': `${wisp.rotate}deg`,
            '--wisp-duration': wisp.duration,
            animationDelay: wisp.delay,
          } as CSSProperties}
        />
      ))}
    </div>
  );
};

const AgentHotspot = ({
  agent,
  selected,
  onSelect,
}: {
  agent: DriftAgent;
  selected: boolean;
  onSelect: (id: string) => void;
}) => {
  const position = hotspotPositions[agent.id] || { x: agent.position.x, y: agent.position.y, anchor: 'center' as const };
  return (
    <button
      type="button"
      onClick={() => onSelect(agent.id)}
      className={`arena-hotspot arena-hotspot-${position.anchor || 'center'} ${selected ? 'arena-hotspot-selected' : ''}`}
      style={{
        left: `${position.x}%`,
        top: `${position.y}%`,
        borderColor: `${agent.accent}9f`,
        boxShadow: selected ? `0 0 0 1px ${agent.accent}, 0 0 26px ${agent.accent}77` : `0 0 18px ${agent.accent}35`,
      }}
      aria-label={`${agent.level} ${agent.name}`}
    >
      <span className="font-mono text-[10px] font-black">{agent.level}</span>
      <span className={`inline-flex items-center gap-1 border px-1.5 py-0.5 font-mono text-[8px] uppercase ${stateMeta[agent.state].tone}`}>
        {stateMeta[agent.state].icon}
        {stateMeta[agent.state].short}
      </span>
      <span className="font-mono text-[8px] font-black uppercase text-white/70">{agent.carCode}</span>
    </button>
  );
};

const SubagentOrbit = ({ agent }: { agent: DriftAgent }) => {
  const position = hotspotPositions[agent.id] || { x: agent.position.x, y: agent.position.y };

  return (
    <div className="arena-subagents" style={{ left: `${position.x}%`, top: `${position.y}%` }} aria-label="Активные субагенты">
      {agent.subagents.map((subagent, index) => {
        const angle = (index / agent.subagents.length) * 360;
        return (
          <span
            key={subagent.id}
            className="arena-subagent-dot"
            style={{
              transform: `rotate(${angle}deg) translateX(78px) rotate(${-angle}deg)`,
              borderColor: subagent.color,
              boxShadow: `0 0 16px ${subagent.color}88`,
            }}
            title={`${subagent.label}: ${subagent.role}`}
          >
            {subagent.label.slice(0, 1)}
          </span>
        );
      })}
    </div>
  );
};

const SelectedInspector = ({ agent }: { agent: DriftAgent }) => (
  <section className="arena-shell-panel p-4">
    <div className="flex items-center justify-between gap-3 border-b border-white/10 pb-3">
      <div>
        <div className="font-mono text-[10px] uppercase tracking-[0.24em] text-white/45">{agent.level}</div>
        <h2 className="mt-1 text-xl font-black">{agent.name}</h2>
      </div>
      <MetricPill label="" value={stateMeta[agent.state].label} state={agent.state} />
    </div>
    <div className="mt-3 grid grid-cols-[88px_1fr] gap-x-4 gap-y-2 text-xs">
      <span className="font-mono uppercase tracking-[0.18em] text-white/35">роль</span>
      <span className="text-right text-white/75">{agent.role}</span>
      <span className="font-mono uppercase tracking-[0.18em] text-white/35">машина</span>
      <span className="text-right text-white/75">{agent.car}</span>
      <span className="font-mono uppercase tracking-[0.18em] text-white/35">субагенты</span>
      <span className="text-right text-white/75">{agent.subagents.length}</span>
    </div>
    <div className="mt-4 grid grid-cols-2 gap-2">
      {agent.subagents.map((subagent) => (
        <div key={subagent.id} className="border border-white/10 bg-black/35 px-2 py-2">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full" style={{ backgroundColor: subagent.color }} />
            <span className="truncate font-mono text-[9px] uppercase">{subagent.label}</span>
          </div>
          <div className="mt-1 truncate text-[10px] text-white/40">{subagent.role}</div>
        </div>
      ))}
    </div>
  </section>
);

const LimitsPanel = ({ snapshot }: { snapshot: DriftWorkflowSnapshot }) => (
  <section className="arena-shell-panel p-4">
    <div className="mb-3 flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.22em] text-amber-100">
      <Timer className="h-4 w-4" />
      Лимиты использования
    </div>
    <div className="space-y-2">
      {snapshot.limits.map((limit) => (
        <div key={limit.agent} className="grid grid-cols-[1fr_auto] gap-3 border border-white/10 bg-black/30 px-3 py-2 text-[10px]">
          <div>
            <div className="font-semibold">{limit.agent}</div>
            <div className="mt-0.5 text-white/40">{limit.observed}</div>
          </div>
          <div className="text-right font-mono uppercase text-white/45">
            <div>{limit.remaining}</div>
            <div>{limit.reset}</div>
          </div>
        </div>
      ))}
    </div>
    <div className="mt-3 flex items-start gap-2 border border-amber-industrial/20 bg-amber-industrial/10 p-2 text-[10px] text-amber-100/75">
      <Lock className="mt-0.5 h-3.5 w-3.5 shrink-0" />
      <span>Остатки и сброс не выдумываются, пока провайдеры не отдают числа.</span>
    </div>
  </section>
);

const DiagnosticsPanel = ({
  snapshot,
  loadState,
}: {
  snapshot: DriftWorkflowSnapshot;
  loadState: 'loading' | 'live' | 'fallback';
}) => (
  <section className="arena-shell-panel p-4">
    <div className="mb-3 flex items-center justify-between gap-3 border-b border-white/10 pb-3">
      <h2 className="font-mono text-[10px] uppercase tracking-[0.22em]">Источники данных</h2>
      <span className="font-mono text-[9px] uppercase text-white/35">{loadState === 'live' ? 'live' : loadState}</span>
    </div>
    <div className="space-y-2">
      {snapshot.diagnostics.slice(0, 5).map((item) => (
        <div key={item} className="border border-white/10 bg-black/30 px-3 py-2 text-[10px] text-white/55">
          {item}
        </div>
      ))}
    </div>
    {snapshot.source && (
      <div className="mt-3 grid grid-cols-[86px_1fr] gap-x-3 gap-y-1 border border-cyan-data/20 bg-cyan-data/5 p-2 text-[9px]">
        <span className="font-mono uppercase tracking-[0.16em] text-cyan-data/70">contract</span>
        <span className="truncate text-white/45">{snapshot.source.contractPath}</span>
        <span className="font-mono uppercase tracking-[0.16em] text-cyan-data/70">events</span>
        <span className="truncate text-white/45">{snapshot.source.eventsPath}</span>
        <span className="font-mono uppercase tracking-[0.16em] text-cyan-data/70">final</span>
        <span className="truncate text-white/45">{snapshot.source.finalReportPath || 'нет'}</span>
      </div>
    )}
  </section>
);

const EventPanel = ({ snapshot }: { snapshot: DriftWorkflowSnapshot }) => (
  <section className="arena-shell-panel min-h-0 p-4">
    <div className="mb-3 flex items-center justify-between gap-3 border-b border-white/10 pb-3">
      <h2 className="font-mono text-[10px] uppercase tracking-[0.22em]">Аудит событий</h2>
      <span className="font-mono text-[9px] uppercase text-white/35">events.jsonl</span>
    </div>
    <div className="space-y-2">
      {snapshot.events.map((event) => (
        <div key={event.id} className="grid grid-cols-[44px_1fr_auto] items-center gap-3 border border-white/10 bg-black/30 px-3 py-2">
          <span className="font-mono text-[10px] text-cyan-data">{event.time}</span>
          <div className="min-w-0">
            <div className="truncate text-xs font-semibold">{event.event}</div>
            <div className="truncate text-[10px] text-white/40">{event.level} · {event.agent}</div>
          </div>
          <span className="font-mono text-[9px] uppercase text-white/45">{decisionLabels[event.decision]}</span>
        </div>
      ))}
    </div>
  </section>
);

export default DriftWorkflowDashboard;
