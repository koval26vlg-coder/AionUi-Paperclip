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
}
