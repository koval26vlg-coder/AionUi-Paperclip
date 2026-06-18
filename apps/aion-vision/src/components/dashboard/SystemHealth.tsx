import { type ReactNode } from 'react';
import { Activity, Brain, Type, Database, AlertTriangle } from 'lucide-react';
import type { SystemHealth as SystemHealthData } from '../../types/dashboard';

interface SystemHealthProps {
  health?: SystemHealthData;
}

type Tone = 'ok' | 'warn' | 'bad';

const toneClass: Record<Tone, string> = {
  ok: 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]',
  warn: 'bg-amber-industrial shadow-[0_0_8px_rgba(245,158,11,0.5)]',
  bad: 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]',
};

function Row({
  icon,
  label,
  value,
  tone,
}: {
  icon: ReactNode;
  label: string;
  value: string;
  tone: Tone;
}) {
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className={`w-1.5 h-1.5 rounded-full ${toneClass[tone]}`}></span>
        <div className="flex items-center gap-2 text-white/40">{icon}</div>
        <span className="text-[10px] font-mono uppercase tracking-wider text-white/60">{label}</span>
      </div>
      <span className="text-[10px] font-mono uppercase text-white/80">{value}</span>
    </div>
  );
}

export default function SystemHealth({ health }: SystemHealthProps) {
  if (!health) return null;

  const watcherTone: Tone =
    health.watcher.status === 'ok' ? 'ok' : health.watcher.status === 'stale' ? 'bad' : 'warn';
  const watcherValue =
    health.watcher.status === 'ok'
      ? `жив (${health.watcher.ageSeconds}с)`
      : health.watcher.status === 'stale'
        ? `завис (${health.watcher.ageSeconds}с)`
        : health.watcher.status === 'missing'
          ? 'не запущен'
          : 'неизвестно';

  const searchTone: Tone = health.search.ollama ? 'ok' : 'warn';

  const backupTone: Tone =
    health.backup.status === 'ok' ? 'ok' : health.backup.status === 'stale' ? 'warn' : 'bad';
  const backupValue =
    health.backup.status === 'missing'
      ? 'нет копий'
      : `${health.backup.last ?? '—'} (${health.backup.count})`;

  return (
    <section className="bg-white/5 border border-white/10 p-6 rounded-sm space-y-4">
      <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold flex items-center gap-2">
        Здоровье системы
        {(watcherTone === 'bad' || backupTone === 'bad') && (
          <AlertTriangle className="w-3.5 h-3.5 text-red-500" />
        )}
      </h2>
      <div className="space-y-3">
        <Row
          icon={<Activity className="w-3 h-3" />}
          label="Наблюдатель"
          value={watcherValue}
          tone={watcherTone}
        />
        <Row
          icon={
            health.search.ollama ? <Brain className="w-3 h-3" /> : <Type className="w-3 h-3" />
          }
          label="Поиск"
          value={health.search.ollama ? 'семантика' : 'текст (FTS5)'}
          tone={searchTone}
        />
        <Row
          icon={<Database className="w-3 h-3" />}
          label="Бэкап БД"
          value={backupValue}
          tone={backupTone}
        />
      </div>
    </section>
  );
}
