import type { DriftWorkflowSnapshot } from '../types/driftWorkflow';

export const DRIFT_WORKFLOW_FALLBACK: DriftWorkflowSnapshot = {
  workflowId: '2026-06-20-103732-814300-drift-workflow-dashboard-prototype',
  title: 'Прототип панели управления дрифт-процессом',
  state: 'done',
  currentLevel: 'L5',
  allowedNextAgents: [],
  referenceRender: '/drift-arena-tuned-kei-ru.png',
  diagnostics: [
    'DEF-04: режим печати у Antigravity вернул служебный вывод готовности для длинных пакетов задачи.',
    'UI работает только на чтение: изменения workflow остаются в tools/agent_workflow.py.',
    'Claude Code L5 зафиксирован с executor=Codex: компактный CLI-проход завершился timeout, предыдущий прогон уперся в бюджет.',
    'Остатки и сброс лимитов неизвестны, пока вручную не настроены лимиты аккаунтов.',
  ],
  agents: [
    {
      id: 'mimo',
      level: 'L1.0',
      name: 'MiMo AUTO',
      role: 'AUTO-первичный проход',
      car: 'Autozam AZ-1 / Suzuki Cappuccino tuned kei scout',
      carCode: 'kei',
      state: 'done',
      color: '#f5f5f4',
      accent: '#f59e0b',
      position: { x: 24, y: 22, rotate: -8 },
      subagents: [
        { id: 'mimo-intake-scanner', label: 'вход', role: 'сканирование постановки', state: 'done', color: '#fbbf24' },
        { id: 'mimo-hypothesis-generator', label: 'гипотезы', role: 'первые варианты', state: 'done', color: '#fde68a' },
        { id: 'mimo-risk-sentinel', label: 'риски', role: 'очевидные риски', state: 'done', color: '#fb923c' },
      ],
    },
    {
      id: 'antigravity-l1',
      level: 'L1.1',
      name: 'Antigravity CLI',
      role: 'резервная исследовательская проверка',
      car: 'Toyota AE86 Trueno',
      carCode: 'AE86',
      state: 'done',
      color: '#1d4ed8',
      accent: '#38bdf8',
      position: { x: 66, y: 20, rotate: 7 },
      subagents: [
        { id: 'ag-source', label: 'источник', role: 'проверка источников', state: 'done', color: '#38bdf8' },
        { id: 'ag-filter', label: 'фильтр', role: 'фильтр шума', state: 'done', color: '#818cf8' },
        { id: 'ag-editor', label: 'передача', role: 'редактор передачи', state: 'done', color: '#22d3ee' },
      ],
    },
    {
      id: 'antigravity-l2',
      level: 'L2',
      name: 'Antigravity CLI',
      role: 'резервная инженерная проверка',
      car: 'Nissan 180SX Type X',
      carCode: '180SX',
      state: 'done',
      color: '#2563eb',
      accent: '#60a5fa',
      position: { x: 73, y: 47, rotate: 18 },
      subagents: [
        { id: 'ag-engineering', label: 'ревью', role: 'инженерная проверка', state: 'done', color: '#60a5fa' },
        { id: 'ag-edge', label: 'край', role: 'поиск крайних случаев', state: 'done', color: '#93c5fd' },
      ],
    },
    {
      id: 'codex-l3',
      level: 'L3',
      name: 'Codex',
      role: 'реализация и тесты',
      car: 'Toyota Chaser JZX100',
      carCode: 'JZX100',
      state: 'done',
      color: '#27272a',
      accent: '#ef4444',
      position: { x: 50, y: 48, rotate: -14 },
      subagents: [
        { id: 'codex-decomposer', label: 'декомп.', role: 'план реализации', state: 'done', color: '#ef4444' },
        { id: 'codex-test-planner', label: 'тесты', role: 'план тестов', state: 'done', color: '#f97316' },
        { id: 'codex-automation', label: 'авто', role: 'сборка автоматизации', state: 'done', color: '#22d3ee' },
        { id: 'codex-integration', label: 'интегр.', role: 'проверка интеграции', state: 'done', color: '#a78bfa' },
      ],
    },
    {
      id: 'codex-l4',
      level: 'L4',
      name: 'Codex',
      role: 'архитектурный синтез',
      car: 'Nissan Silvia S15',
      carCode: 'S15',
      state: 'done',
      color: '#7f1d1d',
      accent: '#fb7185',
      position: { x: 25, y: 78, rotate: 4 },
      subagents: [
        { id: 'codex-architecture', label: 'архит.', role: 'архитектурный синтез', state: 'done', color: '#fb7185' },
        { id: 'codex-risk', label: 'риски', role: 'контроль рисков', state: 'done', color: '#f97316' },
      ],
    },
    {
      id: 'claude-l5',
      level: 'L5',
      name: 'Claude Code',
      role: 'финальное техническое заключение',
      car: 'Toyota Supra A80, легенда дрифта',
      carCode: 'A80',
      state: 'done',
      color: '#f8fafc',
      accent: '#a855f7',
      position: { x: 68, y: 78, rotate: -5 },
      subagents: [
        { id: 'claude-summary', label: 'итог', role: 'итог для руководителя', state: 'done', color: '#a855f7' },
        { id: 'claude-verify', label: 'проверка', role: 'техническая проверка', state: 'done', color: '#22d3ee' },
        { id: 'claude-distortion', label: 'аудит', role: 'аудит без искажений', state: 'done', color: '#84cc16' },
      ],
    },
  ],
  events: [
    { id: 'e1', time: '10:37', agent: 'Codex', event: 'задача создана', level: 'корень', decision: 'approve' },
    { id: 'e2', time: '10:41', agent: 'MiMo AUTO', event: 'L1.0 сдан', level: 'L1.0', decision: 'approve' },
    { id: 'e3', time: '10:46', agent: 'Antigravity CLI', event: 'невалидный вывод печати', level: 'L1.1', decision: 'diagnose' },
    { id: 'e4', time: '10:52', agent: 'Codex', event: 'патч обертки DEF-04', level: 'L1.1', decision: 'diagnose' },
    { id: 'e5', time: '10:56', agent: 'Codex', event: 'старт реализации', level: 'L3', decision: 'pending' },
    { id: 'e6', time: '18:36', agent: 'Claude Code', event: 'ревизия car policy', level: 'L4', decision: 'diagnose' },
    { id: 'e7', time: '18:48', agent: 'Codex', event: 'car policy исправлена', level: 'L4', decision: 'approve' },
    { id: 'e8', time: '18:57', agent: 'Claude Code', event: 'final-report принят', level: 'L5', decision: 'approve' },
  ],
  limits: [
    { agent: 'Codex', observed: 'локальная дельта видна', remaining: 'неизвестно', reset: 'неизвестно', status: 'partial' },
    { agent: 'Claude Code', observed: 'локальный расход за 7 дней виден', remaining: 'неизвестно', reset: 'неизвестно', status: 'partial' },
    { agent: 'MiMo', observed: 'токены и стоимость видны', remaining: 'неизвестно', reset: 'неизвестно', status: 'partial' },
    { agent: 'Antigravity CLI', observed: 'только число записей локальной базы диалогов', remaining: 'неизвестно', reset: 'неизвестно', status: 'unknown' },
  ],
};

export async function loadDriftWorkflowSnapshot(): Promise<DriftWorkflowSnapshot> {
  const apiResponse = await fetch('/api/drift-workflow', { cache: 'no-store' }).catch(() => null);
  if (apiResponse?.ok) {
    return apiResponse.json() as Promise<DriftWorkflowSnapshot>;
  }

  const staticResponse = await fetch('/drift-workflow-data.json', { cache: 'no-store' }).catch(() => null);
  if (staticResponse?.ok) {
    return staticResponse.json() as Promise<DriftWorkflowSnapshot>;
  }

  return {
    ...DRIFT_WORKFLOW_FALLBACK,
    diagnostics: [
      'fallback fixture: live /api/drift-workflow недоступен',
      ...DRIFT_WORKFLOW_FALLBACK.diagnostics,
    ],
  };
}
