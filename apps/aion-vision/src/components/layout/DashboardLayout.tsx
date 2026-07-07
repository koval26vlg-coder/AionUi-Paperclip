import { LayoutDashboard, Database, Activity, BriefcaseBusiness, Cpu, Menu, Route } from 'lucide-react';
import { motion } from 'framer-motion';

export type DashboardView = 'drift' | 'overview' | 'hh-booster' | 'hh-booster-public';

interface DashboardLayoutProps {
  children: React.ReactNode;
  statusLabel: string;
  generatedAt?: string;
  activeView?: DashboardView;
  onViewChange?: (view: DashboardView) => void;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  statusLabel,
  generatedAt,
  activeView = 'overview',
  onViewChange,
}) => {
  return (
    <div className="min-h-screen bg-background text-white flex flex-col lg:flex-row overflow-hidden">
      {/* Side Navigation */}
      <aside className="w-full lg:w-64 border-b lg:border-b-0 lg:border-r border-white/10 bg-background/50 backdrop-blur-xl flex lg:flex-col z-20">
        <div className="p-4 lg:p-6 border-r lg:border-r-0 lg:border-b border-white/10 shrink-0">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-amber-industrial rounded-sm flex items-center justify-center">
              <Cpu className="w-5 h-5 text-black" />
            </div>
            <h1 className="hidden sm:block text-xl font-bold tracking-tighter uppercase italic">Aion Vision</h1>
          </div>
        </div>
        
        <nav className="flex-1 p-3 lg:p-4 flex lg:block gap-2 lg:space-y-2 overflow-x-auto">
          <NavItem
            icon={<Route className="w-5 h-5" />}
            label="Drift workflow"
            active={activeView === 'drift'}
            onClick={() => onViewChange?.('drift')}
          />
          <NavItem
            icon={<LayoutDashboard className="w-5 h-5" />}
            label="Обзор SML"
            active={activeView === 'overview'}
            onClick={() => onViewChange?.('overview')}
          />
          <NavItem
            icon={<BriefcaseBusiness className="w-5 h-5" />}
            label="HH Booster"
            active={activeView === 'hh-booster'}
            onClick={() => onViewChange?.('hh-booster')}
          />
          <NavItem icon={<Activity className="w-5 h-5" />} label="Потоки SML" />
          <NavItem icon={<Database className="w-5 h-5" />} label="Источники памяти" />
        </nav>
        
        <div className="hidden lg:block p-4 border-t border-white/10 opacity-50 text-[10px] font-mono tracking-widest uppercase">
Система Vanguard v1.0.0
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 min-w-0 relative overflow-y-auto">
        {/* Kinetic Background */}
        <div className="absolute inset-0 kinetic-bg pointer-events-none opacity-30 z-0"></div>
        
        {/* Header */}
        <header className="sticky top-0 min-h-16 border-b border-white/10 bg-background/80 backdrop-blur-md flex items-center justify-between gap-4 px-4 lg:px-8 py-3 z-10">
          <div className="flex items-center gap-4">
            <Menu className="w-5 h-5 opacity-50 cursor-pointer lg:hidden" />
            <div className="flex flex-wrap gap-2 text-[10px] font-mono uppercase tracking-widest opacity-50">
              <span>Статус:</span>
              <span className="text-cyan-data">{statusLabel}</span>
              {generatedAt && <span>{new Date(generatedAt).toLocaleTimeString('ru-RU')}</span>}
            </div>
          </div>
          
          <div className="w-8 h-8 rounded-full bg-white/10 border border-white/20 flex items-center justify-center">
            <div className="w-2 h-2 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]"></div>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-4 lg:p-8 relative z-10">
          {children}
        </div>
      </main>
    </div>
  );
};

const NavItem = ({
  icon,
  label,
  active = false,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  active?: boolean;
  onClick?: () => void;
}) => (
  <motion.button
    type="button"
    whileHover={{ x: 4 }}
    onClick={onClick}
    className={`shrink-0 lg:w-full flex items-center gap-3 px-3 lg:px-4 py-3 rounded-sm cursor-pointer transition-colors text-left ${active ? 'bg-amber-industrial text-black font-bold' : 'hover:bg-white/5 text-white/60'}`}
  >
    {icon}
    <span className="text-xs lg:text-sm uppercase tracking-wide whitespace-nowrap">{label}</span>
  </motion.button>
);

export default DashboardLayout;
