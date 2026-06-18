import { LayoutDashboard, Database, Activity, Cpu, Menu } from 'lucide-react';
import { motion } from 'framer-motion';

interface DashboardLayoutProps {
  children: React.ReactNode;
  statusLabel: string;
  generatedAt?: string;
}

const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children, statusLabel, generatedAt }) => {
  return (
    <div className="min-h-screen bg-background text-white flex overflow-hidden">
      {/* Side Navigation */}
      <aside className="w-64 border-r border-white/10 bg-background/50 backdrop-blur-xl flex flex-col z-20">
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-amber-industrial rounded-sm flex items-center justify-center">
              <Cpu className="w-5 h-5 text-black" />
            </div>
            <h1 className="text-xl font-bold tracking-tighter uppercase italic">Aion Vision</h1>
          </div>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          <NavItem icon={<LayoutDashboard className="w-5 h-5" />} label="Обзор" active />
          <NavItem icon={<Activity className="w-5 h-5" />} label="Потоки SML" />
          <NavItem icon={<Database className="w-5 h-5" />} label="Источники памяти" />
        </nav>
        
        <div className="p-4 border-t border-white/10 opacity-50 text-[10px] font-mono tracking-widest uppercase">
Система Vanguard v1.0.0
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 relative overflow-y-auto">
        {/* Kinetic Background */}
        <div className="absolute inset-0 kinetic-bg pointer-events-none opacity-30 z-0"></div>
        
        {/* Header */}
        <header className="sticky top-0 h-16 border-b border-white/10 bg-background/80 backdrop-blur-md flex items-center justify-between px-8 z-10">
          <div className="flex items-center gap-4">
            <Menu className="w-5 h-5 opacity-50 cursor-pointer lg:hidden" />
            <div className="flex gap-2 text-[10px] font-mono uppercase tracking-widest opacity-50">
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
        <div className="p-8 relative z-10">
          {children}
        </div>
      </main>
    </div>
  );
};

const NavItem = ({ icon, label, active = false }: { icon: React.ReactNode, label: string, active?: boolean }) => (
  <motion.div 
    whileHover={{ x: 4 }}
    className={`flex items-center gap-3 px-4 py-3 rounded-sm cursor-pointer transition-colors ${active ? 'bg-amber-industrial text-black font-bold' : 'hover:bg-white/5 text-white/60'}`}
  >
    {icon}
    <span className="text-sm uppercase tracking-wide">{label}</span>
  </motion.div>
);

export default DashboardLayout;
