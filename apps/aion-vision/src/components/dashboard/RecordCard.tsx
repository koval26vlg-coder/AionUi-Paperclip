import React from 'react';
import { motion } from 'framer-motion';
import { User, Calendar } from 'lucide-react';

interface RecordCardProps {
  id: string;
  type: string;
  content: string;
  author: string;
  date: string;
  delay?: number;
}

const RecordCard: React.FC<RecordCardProps> = ({ id, type, content, author, date, delay = 0 }) => {
  return (
    <motion.div 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      className="bg-white/5 border border-white/10 p-6 rounded-sm hover:bg-white/[0.07] transition-colors relative overflow-hidden group"
    >
      <div className="absolute top-0 right-0 p-1 bg-white/10 text-[8px] font-mono uppercase tracking-tighter opacity-50 group-hover:opacity-100">
        ID_{id.toUpperCase()}
      </div>

      <div className="flex items-center gap-3 mb-4">
        <span className={`w-2 h-2 rounded-full ${getTypeColor(type)}`}></span>
        <span className="text-[10px] font-mono uppercase tracking-widest font-bold">{type}</span>
      </div>

      <div className="space-y-4">
        <div className="text-sm leading-relaxed text-white/80 font-mono whitespace-pre-wrap">
          {content}
        </div>

        <div className="flex items-center gap-6 border-t border-white/5 pt-4 opacity-50">
          <div className="flex items-center gap-2">
            <User className="w-3 h-3" />
            <span className="text-[10px] font-mono uppercase">{author}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="w-3 h-3" />
            <span className="text-[10px] font-mono uppercase">{new Date(date).toLocaleDateString()}</span>
          </div>
        </div>
      </div>
      
      <div className="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-white/5 to-transparent"></div>
    </motion.div>
  );
};

const getTypeColor = (type: string) => {
  switch (type.toLowerCase()) {
    case 'agent_log': return 'bg-cyan-data shadow-[0_0_8px_rgba(6,182,212,0.5)]';
    case 'decision': return 'bg-amber-industrial shadow-[0_0_8px_rgba(245,158,11,0.5)]';
    case 'fact': return 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]';
    default: return 'bg-white/50';
  }
};

export default RecordCard;
