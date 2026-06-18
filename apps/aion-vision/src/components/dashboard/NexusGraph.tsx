import { motion } from 'framer-motion';
import type { NexusNode, NexusLink } from '../../types/dashboard';

interface NexusGraphProps {
  nodes: NexusNode[];
  links: NexusLink[];
}

export default function NexusGraph({ nodes, links }: NexusGraphProps) {
  // Защита от пустого графа: без узлов круговая раскладка дала бы
  // деление на ноль и NaN-координаты — SVG молча отрисовался бы пустым.
  if (nodes.length === 0) {
    return (
      <div className="bg-white/5 border border-white/10 p-6 rounded-sm text-center">
        <p className="text-[10px] font-mono uppercase tracking-widest text-white/30 py-8">
          Нет данных графа связей
        </p>
      </div>
    );
  }

  // Простая круговая раскладка для визуализации связей
  const radius = 120;
  const centerX = 160;
  const centerY = 160;

  const nodePositions = nodes.reduce((acc, node, idx) => {
    const angle = (idx / nodes.length) * 2 * Math.PI;
    acc[node.id] = {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle),
    };
    return acc;
  }, {} as Record<string, { x: number; y: number }>);

  return (
    <div className="bg-white/5 border border-white/10 p-6 rounded-sm relative overflow-hidden group">
      <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_center,rgba(0,255,255,0.05)_0%,transparent_70%)] opacity-0 group-hover:opacity-100 transition-opacity duration-700"></div>
      
      <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold mb-6 flex justify-between items-center">
        Граф связей
        <span className="text-[10px] text-cyan-data/50 font-normal">Активные нейросвязи</span>
      </h2>

      <div className="relative aspect-square max-w-[320px] mx-auto">
        <svg viewBox="0 0 320 320" className="w-full h-full drop-shadow-[0_0_8px_rgba(0,255,255,0.2)]">
          {/* Линии связей */}
          {links.map((link, idx) => {
            const start = nodePositions[link.source];
            const end = nodePositions[link.target];
            if (!start || !end) return null;

            return (
              <motion.line
                key={`link-${idx}`}
                x1={start.x}
                y1={start.y}
                x2={end.x}
                y2={end.y}
                stroke={link.type === 'supersede' ? '#F59E0B' : '#00FFFF'}
                strokeWidth={Math.min(link.weight, 4)}
                strokeOpacity={0.3}
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 0.3 }}
                transition={{ duration: 1.5, delay: idx * 0.1 }}
              />
            );
          })}

          {/* Узлы агентов */}
          {nodes.map((node, idx) => {
            const pos = nodePositions[node.id];
            return (
              <motion.g
                key={node.id}
                initial={{ scale: 0, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ type: 'spring', damping: 12, delay: idx * 0.1 }}
              >
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={8 + Math.sqrt(node.records)}
                  className="fill-black stroke-cyan-data stroke-1"
                />
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r={2}
                  className="fill-cyan-data animate-pulse"
                />
                <text
                  x={pos.x}
                  y={pos.y + 25}
                  textAnchor="middle"
                  className="fill-white/60 text-[8px] font-mono uppercase tracking-tighter"
                >
                  {node.id}
                </text>
              </motion.g>
            );
          })}
        </svg>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-[9px] font-mono text-cyan-data uppercase">
            <div className="w-2 h-[1px] bg-cyan-data"></div> Сотрудничество
          </div>
          <p className="text-[8px] text-white/30 font-mono italic">Общий доступ к контексту</p>
        </div>
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-[9px] font-mono text-amber-industrial uppercase">
            <div className="w-2 h-[1px] bg-amber-industrial"></div> Эволюция
          </div>
          <p className="text-[8px] text-white/30 font-mono italic">Замещённые записи</p>
        </div>
      </div>
    </div>
  );
}
