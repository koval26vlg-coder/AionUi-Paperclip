import type React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { SmlDailyActivity } from '../../types/dashboard';

interface AutomationPulseProps {
  data: SmlDailyActivity[];
}

const AutomationPulse: React.FC<AutomationPulseProps> = ({ data }) => {
  const chartData = data.map((item) => ({
    name: item.date.slice(5),
    total: item.total,
    current: item.current,
  }));

  return (
    <div className="h-[300px] w-full bg-white/5 border border-white/10 p-6 rounded-sm">
      <h3 className="text-[10px] font-mono uppercase tracking-[0.3em] opacity-50 mb-6">Динамика SML записей</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
          <XAxis 
            dataKey="name" 
            stroke="#ffffff50" 
            fontSize={10} 
            tickLine={false} 
            axisLine={false}
          />
          <YAxis 
            stroke="#ffffff50" 
            fontSize={10} 
            tickLine={false} 
            axisLine={false}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0A0A0B', border: '1px solid rgba(255,255,255,0.1)', fontSize: '12px' }}
            itemStyle={{ color: '#fff' }}
          />
          <Line 
            type="monotone" 
            dataKey="total"
            name="Все записи"
            stroke="#06B6D4" 
            strokeWidth={2} 
            dot={{ r: 4, fill: '#06B6D4' }}
            activeDot={{ r: 6, stroke: '#06B6D4', strokeWidth: 0, fill: '#fff' }}
          />
          <Line 
            type="monotone" 
            dataKey="current"
            name="Актуальные"
            stroke="#F59E0B" 
            strokeWidth={2} 
            dot={{ r: 4, fill: '#F59E0B' }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default AutomationPulse;
