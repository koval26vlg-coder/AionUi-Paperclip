import { useState, type FormEvent } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Loader2, Brain, Type } from 'lucide-react';
import { searchMemory, translateType } from '../../lib/dashboardData';
import type { SearchResponse } from '../../types/dashboard';

export default function MemorySearch() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<SearchResponse | null>(null);

  const onSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!query.trim() || loading) return;
    setLoading(true);
    try {
      setResponse(await searchMemory(query, 10));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="bg-white/5 border border-white/10 p-6 rounded-sm space-y-5">
      <div className="flex items-center justify-between border-b border-white/10 pb-4">
        <h2 className="text-sm font-mono uppercase tracking-[0.4em] font-bold">Поиск по памяти</h2>
        {response && response.mode !== 'none' && response.mode !== 'error' && (
          <span className="inline-flex items-center gap-1.5 text-[9px] font-mono uppercase text-white/40">
            {response.mode === 'semantic' ? (
              <><Brain className="w-3 h-3 text-cyan-data" /> семантика</>
            ) : (
              <><Type className="w-3 h-3 text-amber-industrial" /> текст</>
            )}
          </span>
        )}
      </div>

      <form onSubmit={onSubmit} className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Спросить общую память…"
            className="w-full bg-black/40 border border-white/10 rounded-sm py-2.5 pl-10 pr-3 text-sm font-mono text-white/80 placeholder:text-white/25 focus:outline-none focus:border-cyan-data/50 transition-colors"
          />
        </div>
        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="inline-flex items-center gap-2 text-[10px] font-mono uppercase text-cyan-data border border-cyan-data/30 px-4 py-2.5 hover:bg-cyan-data/10 disabled:opacity-40 transition-colors"
        >
          {loading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Search className="w-3 h-3" />}
          Найти
        </button>
      </form>

      <AnimatePresence mode="popLayout">
        {response && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-3"
          >
            {response.mode === 'error' ? (
              <p className="text-xs font-mono text-amber-industrial/80">{response.error}</p>
            ) : response.results.length === 0 ? (
              <p className="text-xs font-mono text-white/40">Ничего не найдено.</p>
            ) : (
              response.results.map((item, idx) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.04 }}
                  className="border-l-2 border-cyan-data/30 pl-4 py-1 group hover:border-cyan-data transition-colors"
                >
                  <div className="flex items-center gap-3 mb-1 text-[9px] font-mono uppercase">
                    <span className="text-cyan-data tracking-widest">{translateType(item.type)}</span>
                    <span className="text-white/30">{item.author}</span>
                    <span className="ml-auto text-amber-industrial/70">
                      {Math.round(item.relevanceScore * 100)}%
                    </span>
                  </div>
                  <p className="text-xs leading-relaxed text-white/70 font-mono">{item.content}</p>
                </motion.div>
              ))
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
}
