export type DriftWorkflowState = 'active' | 'next' | 'waiting' | 'blocked' | 'revision' | 'done';

export interface DriftSubagent {
  id: string;
  label: string;
  role: string;
  state: DriftWorkflowState;
  color: string;
}

export interface DriftAgent {
  id: string;
  level: string;
  name: string;
  role: string;
  car: string;
  carCode: string;
  state: DriftWorkflowState;
  color: string;
  accent: string;
  position: {
    x: number;
    y: number;
    rotate: number;
  };
  subagents: DriftSubagent[];
}

export interface DriftEvent {
  id: string;
  time: string;
  agent: string;
  event: string;
  level: string;
  decision: 'approve' | 'diagnose' | 'pending' | 'blocked';
}

export interface DriftLimit {
  agent: string;
  observed: string;
  remaining: string;
  reset: string;
  status: 'known' | 'partial' | 'unknown';
}

export interface DriftWorkflowSource {
  generatedAt: string;
  workflowDir: string;
  contractPath: string;
  eventsPath: string;
  handoffPath: string | null;
  finalReportPath: string | null;
  limitsConfigPath: string;
  limitsLatestPath: string | null;
}

export interface DriftWorkflowSnapshot {
  workflowId: string;
  title: string;
  state: string;
  currentLevel: string;
  allowedNextAgents: string[];
  referenceRender: string;
  diagnostics: string[];
  agents: DriftAgent[];
  events: DriftEvent[];
  limits: DriftLimit[];
  source?: DriftWorkflowSource;
}
