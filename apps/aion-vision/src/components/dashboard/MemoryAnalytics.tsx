import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { SmlWeeklyActivity, SmlAgent, SmlTypeCount } from '../../types/dashboard';

interface MemoryAnalyticsProps {
  weekly?: SmlWeeklyActivity[];
  agents: SmlAgent[];
  typeCounts: SmlTypeCount[];
}

const AGENT_COLORS = ['#06B6D4', '#F59E0B', '#22C55E', '#A855F7', '#EF4444', '#3B82F6', '#EAB308', '#94A3B8'];

function BreakdownBar({
  label,
  value,
  total,
  color,
}: {
  label: string;
  value: number;
  total: number;
  color: string;
}) {
  const pct = total > 0 ? Math.round((value * 100) / total) : 0;
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-[10px] font-mono uppercase">
        <span className="text-white/60 tracking-wider">{label}</span>
        <span className="text-white/40">{value} · {pct}%</span>
      </div>
      <div className="h-1.5 w-full bg-white/5 rounded-sm overflow-hidden">
        <div
          className="h-full rounded-sm transition-all"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

export default function MemoryAnalytics({ weekly, agents, typeCounts }: MemoryAnalyticsProps) {
  const weekData = (weekly ?? []).map((w) => ({
    name: w.weekStart.slice(5), // MM-DD
    total: w.total,
    current: w.current,
  }));

  const agentsTotal = agents.reduce((acc, a) => acc + a.records, 0);
  const typesTotal = typeCounts.reduce((acc, t) => acc + t.total, 0);

  return (
    <section className="bg-white/5 border border-white/10 p-6 rounded-sm space-y-8">
      <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold border-b border-white/10 pb-4">
        Аналитика памяти
      </h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Тренд по неделям */}
        <div className="lg:col-span-2">
          <h3 className="text-[10px] font-mono uppercase tracking-[0.3em] opacity-50 mb-4">
            Записей по неделям
          </h3>
          {weekData.length ? (
            <div className="h-[220px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={weekData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                  <XAxis dataKey="name" stroke="#ffffff50" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="#ffffff50" fontSize={10} tickLine={false} axisLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0A0A0B', border: '1px solid rgba(255,255,255,0.1)', fontSize: '12px' }}
                    itemStyle={{ color: '#fff' }}
                    cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                  />
                  <Bar dataKey="total" name="Все записи" fill="#06B6D4" radius={[2, 2, 0, 0]} />
                  <Bar dataKey="current" name="Актуальные" fill="#F59E0B" radius={[2, 2, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <p className="text-xs font-mono text-white/30 py-8 text-center">Нет данных по неделям</p>
          )}
        </div>

        {/* Разбивка по агентам */}
        <div className="space-y-3">
          <h3 className="text-[10px] font-mono uppercase tracking-[0.3em] opacity-50 mb-1">
            По агентам
          </h3>
          {agents.map((a, idx) => (
            <BreakdownBar
              key={a.name}
              label={a.name}
              value={a.records}
              total={agentsTotal}
              color={AGENT_COLORS[idx % AGENT_COLORS.length]}
            />
          ))}
        </div>

        {/* Разбивка по типам */}
        <div className="space-y-3">
          <h3 className="text-[10px] font-mono uppercase tracking-[0.3em] opacity-50 mb-1">
            По типам
          </h3>
          {typeCounts.map((t, idx) => (
            <BreakdownBar
              key={t.type}
              label={t.type}
              value={t.total}
              total={typesTotal}
              color={AGENT_COLORS[idx % AGENT_COLORS.length]}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
