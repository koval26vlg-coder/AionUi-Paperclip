import type { DashboardData, SearchResponse } from '../types/dashboard';

export const EMPTY_DASHBOARD_DATA: DashboardData = {
  generatedAt: new Date(0).toISOString(),
  status: {
    state: 'empty',
    label: 'Нет данных',
    message: 'SML данные еще не загружены.',
  },
  totals: {
    recordsTotal: 0,
    currentRecords: 0,
    supersededRecords: 0,
    authorsTotal: 0,
    sourceFilesTotal: 0,
  },
  records: [],
  typeCounts: [],
  dailyActivity: [],
  agents: [],
};

export async function loadDashboardData(): Promise<DashboardData> {
  // Сначала live API (vite middleware /api/sml-dashboard → export-sml-dashboard.py),
  // он отдаёт актуальное состояние БД. Если недоступен (прод-сборка без dev-сервера),
  // откатываемся на статический снимок aion-data.json, который пересобирает watcher.
  const apiResponse = await fetch('/api/sml-dashboard', { cache: 'no-store' }).catch(() => null);
  if (apiResponse?.ok) {
    return apiResponse.json() as Promise<DashboardData>;
  }

  const snapshotResponse = await fetch('/aion-data.json', { cache: 'no-store' }).catch(() => null);
  if (snapshotResponse?.ok) {
    return snapshotResponse.json() as Promise<DashboardData>;
  }

  return EMPTY_DASHBOARD_DATA;
}

export async function searchMemory(query: string, limit = 10): Promise<SearchResponse> {
  const trimmed = query.trim();
  if (!trimmed) {
    return { query: '', mode: 'none', results: [] };
  }
  const url = `/api/search?q=${encodeURIComponent(trimmed)}&limit=${limit}`;
  const response = await fetch(url, { cache: 'no-store' }).catch(() => null);
  if (response?.ok) {
    return response.json() as Promise<SearchResponse>;
  }
  return {
    query: trimmed,
    mode: 'error',
    results: [],
    error: 'Поиск недоступен (нужен запущенный dev-сервер Aion Vision).',
  };
}

export function compactNumber(value: number): string {
  return new Intl.NumberFormat('ru-RU', {
    notation: value >= 1000 ? 'compact' : 'standard',
    maximumFractionDigits: 1,
  }).format(value);
}

export function formatDateTime(value: string | null | undefined): string {
  if (!value) {
    return 'нет данных';
  }
  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}

export function translateType(type: string): string {
  const dict: Record<string, string> = {
    'agent_log': 'Журнал агента',
    'decision': 'Решение',
    'fact': 'Факт',
    'preference': 'Предпочтение',
    'constraint': 'Ограничение',
    'task': 'Задача',
    'task_link': 'Связь задачи',
    'timeline_event': 'Событие',
    'none': 'Нет',
    'error': 'Ошибка',
  };
  return dict[type.toLowerCase()] || type;
}

