export interface SmlRecord {
  id: string;
  type: string;
  content: string;
  author: string;
  date: string;
  createdAt?: string;
  isCurrent?: boolean;
  sourceFile?: string | null;
  sourceLines?: string | null;
  tags?: string[];
}

export interface SmlTypeCount {
  type: string;
  total: number;
  current: number;
}

export interface SmlDailyActivity {
  date: string;
  total: number;
  current: number;
}

export interface SmlWeeklyActivity {
  week: string;
  weekStart: string;
  total: number;
  current: number;
}

export interface SmlAgent {
  name: string;
  records: number;
  lastUpdated: string | null;
  status: string;
}

export interface NexusNode {
  id: string;
  records: number;
}

export interface NexusLink {
  source: string;
  target: string;
  type: 'collab' | 'supersede';
  weight: number;
}

export interface SystemHealth {
  watcher: {
    status: 'ok' | 'stale' | 'missing' | 'unknown';
    ageSeconds: number | null;
    last: string | null;
  };
  search: {
    mode: 'semantic' | 'text';
    ollama: boolean;
  };
  backup: {
    status: 'ok' | 'stale' | 'missing' | 'unknown';
    last: string | null;
    count: number;
  };
}

export interface SearchResultItem {
  id: string;
  type: string;
  author: string;
  date: string;
  isCurrent: boolean;
  content: string;
  relevanceScore: number;
  tags: string[];
}

export interface SearchResponse {
  query: string;
  mode: 'semantic' | 'text' | 'none' | 'error';
  results: SearchResultItem[];
  error?: string;
}

export interface DashboardData {
  generatedAt: string;
  status: {
    state: 'live' | 'empty' | 'error' | string;
    label: string;
    message: string;
  };
  totals: {
    recordsTotal: number;
    currentRecords: number;
    supersededRecords: number;
    authorsTotal: number;
    sourceFilesTotal: number;
  };
  records: SmlRecord[];
  typeCounts: SmlTypeCount[];
  dailyActivity: SmlDailyActivity[];
  agents: SmlAgent[];
  nexusGraph?: {
    nodes: NexusNode[];
    links: NexusLink[];
  };
  weeklyActivity?: SmlWeeklyActivity[];
  health?: SystemHealth;
}
