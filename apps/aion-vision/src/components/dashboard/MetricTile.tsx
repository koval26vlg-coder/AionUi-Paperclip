import { motion } from 'framer-motion';

interface MetricTileProps {
  label: string;
  value: string | number;
  trend?: string;
  icon: React.ReactNode;
  color?: 'amber' | 'cyan';
}

const MetricTile: React.FC<MetricTileProps> = ({ label, value, trend, icon, color = 'cyan' }) => {
  const colorClass = color === 'amber' ? 'text-amber-industrial border-amber-industrial/20' : 'text-cyan-data border-cyan-data/20';
  const glowClass = color === 'amber' ? 'glow-amber' : 'glow-cyan';

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-white/5 border p-6 rounded-sm ${colorClass} ${glowClass}`}
    >
      <div className="flex justify-between items-start mb-4">
        <div className="p-2 bg-white/5 rounded-sm">
          {icon}
        </div>
        {trend && (
          <span className="text-[10px] font-mono uppercase bg-white/10 px-2 py-1 rounded-full">
            {trend}
          </span>
        )}
      </div>
      
      <div className="space-y-1">
        <p className="text-[10px] font-mono uppercase tracking-[0.2em] opacity-50">{label}</p>
        <p className="text-3xl font-bold font-mono tracking-tighter">{value}</p>
      </div>
    </motion.div>
  );
};

export default MetricTile;
