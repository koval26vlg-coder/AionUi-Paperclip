import { useCallback, useMemo, useState } from 'react';
import {
  ArrowRight,
  BriefcaseBusiness,
  CalendarDays,
  Camera,
  CheckCircle2,
  ClipboardCheck,
  Copy,
  Download,
  FileSearch,
  Mail,
  Play,
  RotateCcw,
  ShieldCheck,
  Trash2,
} from 'lucide-react';

type OfferId = 'avatar' | 'audit' | 'response';
type PaymentIntent = 'ready' | 'maybe' | 'not_now';

interface Offer {
  id: OfferId;
  title: string;
  subtitle: string;
  price: number;
  icon: React.ReactNode;
  deliverables: string[];
  testQuestion: string;
}

interface BoosterLead {
  id: string;
  createdAt: string;
  offer: OfferId;
  contact: string;
  role: string;
  intent: PaymentIntent;
  channel: string;
  notes: string;
}

type LeadForm = Omit<BoosterLead, 'id' | 'createdAt'>;

interface ExperimentState {
  startedAt: string | null;
  durationDays: number;
  targetLeads: number;
  targetPaidIntent: number;
  targetChannels: number;
  targetRoles: number;
  targetMinLeadsPerOffer: number;
}

const STORAGE_KEY = 'aion.hhResumeBooster.leads.v1';
const EXPERIMENT_STORAGE_KEY = 'aion.hhResumeBooster.experiment.v1';
const PUBLIC_BASE_STORAGE_KEY = 'aion.hhResumeBooster.publicBaseUrl.v1';
const DAY_MS = 24 * 60 * 60 * 1000;

const defaultExperiment: ExperimentState = {
  startedAt: null,
  durationDays: 14,
  targetLeads: 30,
  targetPaidIntent: 10,
  targetChannels: 2,
  targetRoles: 5,
  targetMinLeadsPerOffer: 5,
};

const offers: Offer[] = [
  {
    id: 'avatar',
    title: 'Аватарка',
    subtitle: 'Проверка фото для резюме и быстрый деловой вариант.',
    price: 199,
    icon: <Camera className="h-5 w-5" />,
    deliverables: ['Оценка кадра', 'Фон и кроп', 'Рекомендация стиля'],
    testQuestion: 'Платят ли за фото отдельно?',
  },
  {
    id: 'audit',
    title: 'Аудит резюме',
    subtitle: 'Фото, заголовок, опыт и блок "о себе" перед откликами.',
    price: 399,
    icon: <FileSearch className="h-5 w-5" />,
    deliverables: ['Score резюме', 'Приоритет правок', 'Версия заголовка'],
    testQuestion: 'Сильнее ли полный аудит?',
  },
  {
    id: 'response',
    title: 'Отклик под вакансию',
    subtitle: 'Резюме, письмо и аргументы под конкретную вакансию.',
    price: 799,
    icon: <BriefcaseBusiness className="h-5 w-5" />,
    deliverables: ['Fit под вакансию', 'Cover letter', 'Checklist отклика'],
    testQuestion: 'Готовы ли платить за пакет?',
  },
];

const intentLabels: Record<PaymentIntent, string> = {
  ready: 'Готов оплатить',
  maybe: 'Интересно, хочу детали',
  not_now: 'Не готов платить',
};

const channelLabels = ['hh.ru', 'Telegram', 'VK', 'Авито Работа', 'Рекомендация', 'Другое'];

const currencyFormatter = new Intl.NumberFormat('ru-RU', {
  style: 'currency',
  currency: 'RUB',
  maximumFractionDigits: 0,
});

const offerRequestText: Record<OfferId, string> = {
  avatar: 'пришли текущее фото/аватарку и ссылку на профиль hh.ru, если удобно',
  audit: 'пришли ссылку на резюме hh.ru или PDF/скрин резюме',
  response: 'пришли ссылку на вакансию и резюме, с которым хочешь откликаться',
};

const offerPromiseText: Record<OfferId, string> = {
  avatar: 'дам короткий разбор первого впечатления и что поменять в фото',
  audit: 'верну 3 главные правки по резюме и формулировкам',
  response: 'соберу позиционирование и черновик отклика под конкретную вакансию',
};

const emptyForm: LeadForm = {
  offer: 'avatar',
  contact: '',
  role: '',
  intent: 'ready',
  channel: 'hh.ru',
  notes: '',
};

function readStoredLeads(): BoosterLead[] {
  if (typeof window === 'undefined') return [];

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.filter(isBoosterLead) : [];
  } catch {
    return [];
  }
}

function readStoredExperiment(): ExperimentState {
  if (typeof window === 'undefined') return defaultExperiment;

  try {
    const raw = window.localStorage.getItem(EXPERIMENT_STORAGE_KEY);
    if (!raw) return defaultExperiment;
    const parsed = JSON.parse(raw) as Partial<ExperimentState>;
    return {
      startedAt: typeof parsed.startedAt === 'string' ? parsed.startedAt : null,
      durationDays: validPositiveNumber(parsed.durationDays, defaultExperiment.durationDays),
      targetLeads: validPositiveNumber(parsed.targetLeads, defaultExperiment.targetLeads),
      targetPaidIntent: validPositiveNumber(parsed.targetPaidIntent, defaultExperiment.targetPaidIntent),
      targetChannels: validPositiveNumber(parsed.targetChannels, defaultExperiment.targetChannels),
      targetRoles: validPositiveNumber(parsed.targetRoles, defaultExperiment.targetRoles),
      targetMinLeadsPerOffer: validPositiveNumber(
        parsed.targetMinLeadsPerOffer,
        defaultExperiment.targetMinLeadsPerOffer,
      ),
    };
  } catch {
    return defaultExperiment;
  }
}

function browserPublicBaseUrl() {
  if (typeof window === 'undefined') return '#hh-booster-public';
  return `${window.location.origin}${window.location.pathname}#hh-booster-public`;
}

function normalizePublicBaseUrl(value: string) {
  const trimmed = value.trim();
  if (!trimmed) return '';
  const withoutTrailingSlash = trimmed.replace(/\/+$/, '');
  if (withoutTrailingSlash.includes('#hh-booster-public')) return withoutTrailingSlash;
  return `${withoutTrailingSlash}/#hh-booster-public`;
}

function readStoredPublicBaseUrl() {
  if (typeof window === 'undefined') return '';

  try {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get('publicBaseUrl') ?? params.get('public_base_url') ?? '';
    if (fromQuery) {
      const normalized = normalizePublicBaseUrl(fromQuery);
      window.localStorage.setItem(PUBLIC_BASE_STORAGE_KEY, normalized);
      return normalized;
    }
    return window.localStorage.getItem(PUBLIC_BASE_STORAGE_KEY) ?? '';
  } catch {
    return '';
  }
}

function coerceExperimentState(value: unknown): ExperimentState | null {
  if (!value || typeof value !== 'object') return null;
  const parsed = value as Partial<ExperimentState>;
  const startedAt = parsed.startedAt === null || typeof parsed.startedAt === 'string' ? parsed.startedAt : null;
  return {
    startedAt,
    durationDays: validPositiveNumber(parsed.durationDays, defaultExperiment.durationDays),
    targetLeads: validPositiveNumber(parsed.targetLeads, defaultExperiment.targetLeads),
    targetPaidIntent: validPositiveNumber(parsed.targetPaidIntent, defaultExperiment.targetPaidIntent),
    targetChannels: validPositiveNumber(parsed.targetChannels, defaultExperiment.targetChannels),
    targetRoles: validPositiveNumber(parsed.targetRoles, defaultExperiment.targetRoles),
    targetMinLeadsPerOffer: validPositiveNumber(
      parsed.targetMinLeadsPerOffer,
      defaultExperiment.targetMinLeadsPerOffer,
    ),
  };
}

function validPositiveNumber(value: unknown, fallback: number) {
  return typeof value === 'number' && Number.isFinite(value) && value > 0 ? value : fallback;
}

function isBoosterLead(value: unknown): value is BoosterLead {
  if (!value || typeof value !== 'object') return false;
  const item = value as Partial<BoosterLead>;
  return (
    typeof item.id === 'string' &&
    typeof item.createdAt === 'string' &&
    isOfferId(item.offer) &&
    typeof item.contact === 'string' &&
    typeof item.role === 'string' &&
    isPaymentIntent(item.intent) &&
    typeof item.channel === 'string' &&
    typeof item.notes === 'string'
  );
}

function isOfferId(value: unknown): value is OfferId {
  return value === 'avatar' || value === 'audit' || value === 'response';
}

function isPaymentIntent(value: unknown): value is PaymentIntent {
  return value === 'ready' || value === 'maybe' || value === 'not_now';
}

function buildMetrics(leads: BoosterLead[]) {
  const byOffer = offers.map((offer) => {
    const offerLeads = leads.filter((lead) => lead.offer === offer.id);
    const paidIntent = offerLeads.filter((lead) => lead.intent === 'ready').length;
    return {
      ...offer,
      leads: offerLeads.length,
      paidIntent,
      rate: offerLeads.length ? Math.round((paidIntent * 100) / offerLeads.length) : 0,
    };
  });

  const totalPaidIntent = byOffer.reduce((sum, offer) => sum + offer.paidIntent, 0);
  const winner = [...byOffer].sort((a, b) => b.paidIntent - a.paidIntent || b.leads - a.leads)[0];
  const uniqueRoles = new Set(leads.map((lead) => lead.role.trim()).filter(Boolean)).size;
  const uniqueChannels = new Set(leads.map((lead) => lead.channel.trim()).filter(Boolean)).size;

  return {
    totalLeads: leads.length,
    totalPaidIntent,
    paidIntentRate: leads.length ? Math.round((totalPaidIntent * 100) / leads.length) : 0,
    uniqueRoles,
    uniqueChannels,
    byOffer,
    winner,
  };
}

function buildExperimentProgress(experiment: ExperimentState, metrics: ReturnType<typeof buildMetrics>) {
  const started = Boolean(experiment.startedAt);
  const startedAt = experiment.startedAt ? new Date(experiment.startedAt) : null;
  const endsAt = startedAt ? new Date(startedAt.getTime() + experiment.durationDays * DAY_MS) : null;
  const elapsedDays = startedAt ? Math.max(0, Math.floor((Date.now() - startedAt.getTime()) / DAY_MS) + 1) : 0;
  const currentDay = started ? Math.min(experiment.durationDays, elapsedDays) : 0;
  const daysLeft = started ? Math.max(0, experiment.durationDays - currentDay) : experiment.durationDays;
  const daysComplete = endsAt ? Date.now() >= endsAt.getTime() : false;
  const leadsReady = metrics.totalLeads >= experiment.targetLeads;
  const paidReady = metrics.totalPaidIntent >= experiment.targetPaidIntent;
  const channelsReady = metrics.uniqueChannels >= experiment.targetChannels;
  const rolesReady = metrics.uniqueRoles >= experiment.targetRoles;
  const offersCovered = metrics.byOffer.filter((offer) => offer.leads >= experiment.targetMinLeadsPerOffer).length;
  const offerCoverageReady = offersCovered === metrics.byOffer.length;
  const decisionReady = daysComplete && leadsReady && paidReady && channelsReady && rolesReady && offerCoverageReady;

  return {
    started,
    startedAt,
    endsAt,
    currentDay,
    daysLeft,
    daysComplete,
    leadsReady,
    paidReady,
    channelsReady,
    rolesReady,
    offersCovered,
    offerCoverageReady,
    decisionReady,
  };
}

function buildDailyMetrics(
  leads: BoosterLead[],
  experiment: ExperimentState,
  progress: ReturnType<typeof buildExperimentProgress>,
  metrics: ReturnType<typeof buildMetrics>,
) {
  const byDayMap = new Map<
    string,
    { date: string; leads: number; paidIntent: number; avatar: number; audit: number; response: number }
  >();

  leads.forEach((lead) => {
    const date = dateKeyFromIso(lead.createdAt);
    const current = byDayMap.get(date) ?? {
      date,
      leads: 0,
      paidIntent: 0,
      avatar: 0,
      audit: 0,
      response: 0,
    };
    current.leads += 1;
    if (lead.intent === 'ready') current.paidIntent += 1;
    current[lead.offer] += 1;
    byDayMap.set(date, current);
  });

  const byDay = [...byDayMap.values()].sort((a, b) => b.date.localeCompare(a.date));
  const todayKey = dateKeyFromDate(new Date());
  const today = byDay.find((item) => item.date === todayKey) ?? {
    date: todayKey,
    leads: 0,
    paidIntent: 0,
    avatar: 0,
    audit: 0,
    response: 0,
  };
  const activeDays = byDay.length;
  const daysAvailable = progress.started
    ? Math.max(0, experiment.durationDays - progress.currentDay + 1)
    : experiment.durationDays;

  return {
    byDay,
    today,
    activeDays,
    averageLeadsPerActiveDay: activeDays ? leads.length / activeDays : 0,
    averagePaidPerActiveDay: activeDays ? metrics.totalPaidIntent / activeDays : 0,
    requiredLeadsPerRemainingDay: daysAvailable
      ? Math.max(0, experiment.targetLeads - metrics.totalLeads) / daysAvailable
      : 0,
    requiredPaidPerRemainingDay: daysAvailable
      ? Math.max(0, experiment.targetPaidIntent - metrics.totalPaidIntent) / daysAvailable
      : 0,
    daysAvailable,
  };
}

function buildConciergeActions(leads: BoosterLead[]) {
  return [...leads]
    .filter((lead) => lead.intent === 'ready' || lead.intent === 'maybe')
    .sort((a, b) => {
      const intentDelta = intentRank(a.intent) - intentRank(b.intent);
      if (intentDelta) return intentDelta;
      const offerDelta = offerRank(a.offer) - offerRank(b.offer);
      if (offerDelta) return offerDelta;
      return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
    })
    .slice(0, 4)
    .map((lead) => ({
      lead,
      priority: lead.intent === 'ready' ? 'P0' : 'P1',
      message: conciergeMessage(lead),
      missingInputs: conciergeMissingInputs(lead),
    }));
}

function intentRank(intent: PaymentIntent) {
  if (intent === 'ready') return 0;
  if (intent === 'maybe') return 1;
  return 2;
}

function offerRank(offer: OfferId) {
  if (offer === 'response') return 0;
  if (offer === 'audit') return 1;
  return 2;
}

function offerById(offerId: OfferId) {
  return offers.find((offer) => offer.id === offerId) ?? offers[0];
}

function conciergeMissingInputs(lead: BoosterLead) {
  const inputs =
    lead.offer === 'response'
      ? ['вакансия', 'резюме']
      : lead.offer === 'audit'
        ? ['резюме']
        : ['фото/профиль'];
  return lead.role.trim() ? inputs : [...inputs, 'роль'];
}

function conciergeMessage(lead: BoosterLead) {
  const offer = offerById(lead.offer);
  const roleText = lead.role.trim() ? ` по роли ${lead.role.trim()}` : '';
  if (lead.intent === 'ready') {
    return (
      `Привет! Спасибо за заявку на ${offer.title.toLowerCase()}${roleText}. ` +
      `Формат стоит ${currencyFormatter.format(offer.price)}. Если актуально, ${offerRequestText[lead.offer]}. ` +
      `После этого ${offerPromiseText[lead.offer]}. Без обещаний гарантированных приглашений, только практичный разбор.`
    );
  }
  return (
    `Привет! Ты отметил интерес к формату ${offer.title.toLowerCase()}${roleText}. ` +
    `Хочу понять, что было бы реально полезно перед оплатой: ${offerRequestText[lead.offer]}. ` +
    'Я коротко скажу, подойдет ли этот формат, и что именно получится на выходе.'
  );
}

function dateKeyFromIso(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'unknown' : dateKeyFromDate(date);
}

function dateKeyFromDate(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatDate(value: Date | null) {
  return value ? value.toLocaleDateString('ru-RU') : 'не начат';
}

function formatDecimal(value: number) {
  return value.toLocaleString('ru-RU', { maximumFractionDigits: 1 });
}

function csvCell(value: string | number) {
  return `"${String(value).replace(/"/g, '""')}"`;
}

async function syncExperimentToServer(nextExperiment: ExperimentState) {
  if (import.meta.env.DEV) return;
  const response = await fetch('/api/hh-booster/experiment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(nextExperiment),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
}

export default function HhBoosterValidation() {
  const [leads, setLeads] = useState<BoosterLead[]>(() => readStoredLeads());
  const [experiment, setExperiment] = useState<ExperimentState>(() => readStoredExperiment());
  const [form, setForm] = useState<LeadForm>(emptyForm);
  const [selectedOffer, setSelectedOffer] = useState<OfferId>('avatar');
  const [publicBaseOverride, setPublicBaseOverride] = useState(() => readStoredPublicBaseUrl());
  const [savedNotice, setSavedNotice] = useState('');

  const metrics = useMemo(() => buildMetrics(leads), [leads]);
  const progress = useMemo(() => buildExperimentProgress(experiment, metrics), [experiment, metrics]);
  const dailyMetrics = useMemo(
    () => buildDailyMetrics(leads, experiment, progress, metrics),
    [experiment, leads, metrics, progress],
  );
  const conciergeActions = useMemo(() => buildConciergeActions(leads), [leads]);
  const publicBaseUrl = useMemo(() => {
    const normalized = normalizePublicBaseUrl(publicBaseOverride);
    return normalized || browserPublicBaseUrl();
  }, [publicBaseOverride]);
  const usingLocalPublicBase = useMemo(() => {
    try {
      const host = new URL(publicBaseUrl.split('#', 1)[0]).hostname;
      return host === '127.0.0.1' || host === 'localhost' || host === '::1';
    } catch {
      return false;
    }
  }, [publicBaseUrl]);
  const publicLink = useCallback(
    (channel: string, offer?: OfferId) =>
      `${publicBaseUrl}?channel=${encodeURIComponent(channel)}${offer ? `&offer=${encodeURIComponent(offer)}` : ''}`,
    [publicBaseUrl],
  );
  const launchLinks = useMemo(
    () =>
      channelLabels.map((channel) => ({
        channel,
        url: publicLink(channel),
      })),
    [publicLink],
  );
  const offerLaunchLinks = useMemo(
    () =>
      offers.flatMap((offer) =>
        channelLabels.map((channel) => ({
          key: `${offer.id}-${channel}`,
          offer: offer.title,
          channel,
          url: publicLink(channel, offer.id),
        })),
      ),
    [publicLink],
  );
  const outreachTexts = useMemo(
    () => [
      {
        title: 'Карьерный чат',
        text:
          'Тестирую маленький сервис для соискателей на hh.ru: проверка фото, резюме и отклика перед отправкой работодателю.\n' +
          `Нужно 5 минут: выбрать формат 199/399/799 руб. и оставить контакт для ручного разбора.\n${publicLink(
            'Telegram',
            'audit',
          )}`,
      },
      {
        title: 'Личное сообщение',
        text:
          'Привет. Я проверяю идею сервиса для hh.ru: фото + резюме + отклик под вакансию.\n' +
          `Можешь выбрать, какой формат был бы реально полезен, и оставить контакт? ${publicLink(
            'Рекомендация',
            'response',
          )}`,
      },
      {
        title: 'VK / пост',
        text:
          'Проверяю спрос на ручной разбор профиля hh.ru: фото, резюме или отклик под конкретную вакансию.\n' +
          `Без обещаний гарантированных приглашений. Нужна честная готовность платить: ${publicLink('VK', 'avatar')}`,
      },
    ],
    [publicLink],
  );

  const persistLeads = (nextLeads: BoosterLead[]) => {
    setLeads(nextLeads);
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(nextLeads));
  };

  const persistExperiment = (nextExperiment: ExperimentState, options: { syncServer?: boolean } = {}) => {
    setExperiment(nextExperiment);
    window.localStorage.setItem(EXPERIMENT_STORAGE_KEY, JSON.stringify(nextExperiment));
    if (options.syncServer !== false) void syncExperimentToServer(nextExperiment).catch(() => undefined);
  };

  const startExperiment = () => {
    persistExperiment({ ...experiment, startedAt: new Date().toISOString() });
  };

  const resetExperiment = () => {
    const confirmed = window.confirm('Сбросить дату старта эксперимента? Заявки останутся на месте.');
    if (confirmed) persistExperiment({ ...experiment, startedAt: null });
  };

  const updateForm = <Key extends keyof LeadForm>(key: Key, value: LeadForm[Key]) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const showNotice = (message: string) => {
    setSavedNotice(message);
    window.setTimeout(() => setSavedNotice(''), 3600);
  };

  const savePublicBaseOverride = (value: string) => {
    const normalized = normalizePublicBaseUrl(value);
    setPublicBaseOverride(normalized);
    if (normalized) {
      window.localStorage.setItem(PUBLIC_BASE_STORAGE_KEY, normalized);
      showNotice('Публичный host сохранен для ссылок.');
    } else {
      window.localStorage.removeItem(PUBLIC_BASE_STORAGE_KEY);
      showNotice('Публичный host сброшен. Ссылки снова строятся от текущей страницы.');
    }
  };

  const copyText = async (value: string, label: string) => {
    try {
      await navigator.clipboard.writeText(value);
      showNotice(`Скопировано: ${label}`);
    } catch {
      showNotice('Не удалось скопировать автоматически. Выдели текст вручную.');
    }
  };

  const selectOffer = (offerId: OfferId) => {
    setSelectedOffer(offerId);
    updateForm('offer', offerId);
    document.getElementById('hh-concierge-form')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const submitLead = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextLead: BoosterLead = {
      ...form,
      id: crypto.randomUUID(),
      createdAt: new Date().toISOString(),
    };
    persistLeads([nextLead, ...leads]);
    setForm({ ...emptyForm, offer: selectedOffer });
    showNotice('Заявка сохранена локально. Данные никуда не отправлялись.');
  };

  const exportJson = () => {
    const payload = {
      experiment: 'hh-resume-booster-validation',
      exportedAt: new Date().toISOString(),
      storageKey: STORAGE_KEY,
      experimentStorageKey: EXPERIMENT_STORAGE_KEY,
      experimentState: experiment,
      experimentProgress: progress,
      metrics,
      dailyMetrics,
      offers: offers.map((offer) => ({
        id: offer.id,
        title: offer.title,
        subtitle: offer.subtitle,
        price: offer.price,
        deliverables: offer.deliverables,
        testQuestion: offer.testQuestion,
      })),
      leads,
    };
    downloadFile(
      `hh-resume-booster-leads-${new Date().toISOString().slice(0, 10)}.json`,
      JSON.stringify(payload, null, 2),
      'application/json',
    );
  };

  const exportCsv = () => {
    const header = ['id', 'createdAt', 'offer', 'contact', 'role', 'intent', 'channel', 'notes'];
    const rows = leads.map((lead) =>
      [
        lead.id,
        lead.createdAt,
        lead.offer,
        lead.contact,
        lead.role,
        lead.intent,
        lead.channel,
        lead.notes,
      ]
        .map(csvCell)
        .join(','),
    );
    downloadFile(
      `hh-resume-booster-leads-${new Date().toISOString().slice(0, 10)}.csv`,
      `\uFEFF${[header.map(csvCell).join(','), ...rows].join('\n')}`,
      'text/csv;charset=utf-8',
    );
  };

  const downloadFile = (fileName: string, content: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  };

  const clearLeads = () => {
    if (!leads.length) return;
    const confirmed = window.confirm('Очистить локальные заявки HH Resume Booster?');
    if (confirmed) persistLeads([]);
  };

  const importServerLeads = async () => {
    try {
      const [response, experimentResponse] = await Promise.all([
        fetch('/api/hh-booster/leads?limit=5000', { cache: 'no-store' }),
        fetch('/api/hh-booster/experiment', { cache: 'no-store' }).catch(() => null),
      ]);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = (await response.json()) as { leads?: unknown[] };
      const serverLeads = Array.isArray(payload.leads) ? payload.leads.filter(isBoosterLead) : [];
      const byId = new Map<string, BoosterLead>();
      [...serverLeads, ...leads].forEach((lead) => {
        if (!byId.has(lead.id)) byId.set(lead.id, lead);
      });
      const merged = [...byId.values()].sort(
        (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime(),
      );
      persistLeads(merged);
      let experimentImported = false;
      if (experimentResponse?.ok) {
        const experimentPayload = (await experimentResponse.json()) as { experiment?: unknown };
        const serverExperiment = coerceExperimentState(experimentPayload.experiment);
        if (serverExperiment) {
          persistExperiment(serverExperiment, { syncServer: false });
          experimentImported = true;
        }
      }
      showNotice(
        `Импортировано серверных заявок: ${serverLeads.length}. Всего в панели: ${merged.length}.` +
          (experimentImported ? ' Дата старта обновлена с сервера.' : ''),
      );
    } catch {
      showNotice('Серверный импорт недоступен. В dev-режиме используй localStorage или JSON/CSV export.');
    }
  };

  return (
    <div className="mx-auto flex max-w-7xl flex-col gap-8 text-white">
      <section className="grid min-h-[680px] grid-cols-1 gap-8 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="flex flex-col justify-between gap-8 border border-white/10 bg-[#07090d]/80 p-6 shadow-2xl shadow-black/30 md:p-8">
          <div className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3 text-xs font-mono uppercase tracking-[0.24em] text-cyan-data">
                <ShieldCheck className="h-4 w-4" />
                2-недельный тест спроса
              </div>
              <div className="flex flex-wrap gap-2">
                <a href="#hh-booster-public" className="booster-tool-button">
                  <ArrowRight className="h-4 w-4" />
                  Публичная форма
                </a>
                <button type="button" onClick={startExperiment} className="booster-tool-button">
                  <Play className="h-4 w-4" />
                  {progress.started ? 'Перезапуск' : 'Старт теста'}
                </button>
                <button type="button" onClick={resetExperiment} className="booster-tool-button">
                  <RotateCcw className="h-4 w-4" />
                  Сброс даты
                </button>
              </div>
            </div>
            <div className="max-w-3xl space-y-5">
              <h1 className="text-4xl font-black leading-[0.96] tracking-normal text-white md:text-6xl">
                HH Resume Booster
              </h1>
              <p className="text-lg leading-8 text-white/68 md:text-xl">
                Проверяем, за что соискатели готовы платить: отдельную аватарку,
                полный аудит резюме или пакет отклика под конкретную вакансию.
              </p>
            </div>

            <section className="grid gap-4 border border-white/10 bg-black/20 p-4 md:grid-cols-[1fr_1.2fr]">
              <div className="flex items-start gap-3">
                <div className="grid h-10 w-10 shrink-0 place-items-center border border-cyan-data/30 bg-cyan-data/10 text-cyan-data">
                  <CalendarDays className="h-5 w-5" />
                </div>
                <div>
                  <p className="font-mono text-xs uppercase tracking-[0.18em] text-white/38">Статус эксперимента</p>
                  <h2 className="mt-2 text-2xl font-bold">
                    {progress.started ? `День ${progress.currentDay} из ${experiment.durationDays}` : 'Тест еще не начат'}
                  </h2>
                  <p className="mt-2 text-sm leading-6 text-white/54">
                    Старт: {formatDate(progress.startedAt)} · Финиш: {formatDate(progress.endsAt)}
                    <br />
                    Минимум на оффер: {experiment.targetMinLeadsPerOffer}
                  </p>
                </div>
              </div>
              <div className="grid gap-3 md:grid-cols-5">
                <GatePill label="Лиды" value={metrics.totalLeads} target={experiment.targetLeads} ready={progress.leadsReady} />
                <GatePill label="Paid" value={metrics.totalPaidIntent} target={experiment.targetPaidIntent} ready={progress.paidReady} />
                <GatePill label="Каналы" value={metrics.uniqueChannels} target={experiment.targetChannels} ready={progress.channelsReady} />
                <GatePill label="Роли" value={metrics.uniqueRoles} target={experiment.targetRoles} ready={progress.rolesReady} />
                <GatePill label="Офферы" value={progress.offersCovered} target={offers.length} ready={progress.offerCoverageReady} />
              </div>
            </section>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
              {offers.map((offer) => {
                const isSelected = selectedOffer === offer.id;
                return (
                  <button
                    type="button"
                    key={offer.id}
                    onClick={() => selectOffer(offer.id)}
                    className={`group flex min-h-[220px] flex-col justify-between border p-5 text-left transition-colors ${
                      isSelected
                        ? 'border-amber-industrial bg-amber-industrial text-black'
                        : 'border-white/10 bg-white/[0.035] hover:border-cyan-data/60 hover:bg-white/[0.06]'
                    }`}
                  >
                    <div className="space-y-4">
                      <div className="flex items-start justify-between gap-4">
                        <div
                          className={`grid h-10 w-10 place-items-center border ${
                            isSelected ? 'border-black/25 bg-black/10' : 'border-white/10 bg-black/30 text-cyan-data'
                          }`}
                        >
                          {offer.icon}
                        </div>
                        <span className="font-mono text-sm font-bold">
                          {currencyFormatter.format(offer.price)}
                        </span>
                      </div>
                      <div>
                        <h2 className="text-xl font-bold">{offer.title}</h2>
                        <p className={`mt-2 text-sm leading-6 ${isSelected ? 'text-black/70' : 'text-white/58'}`}>
                          {offer.subtitle}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center justify-between pt-5 text-xs font-mono uppercase tracking-[0.16em]">
                      <span>{offer.testQuestion}</span>
                      <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 border-t border-white/10 pt-6 md:grid-cols-3">
            <Metric label="Заявки" value={metrics.totalLeads.toString()} />
            <Metric label="Paid intent" value={metrics.totalPaidIntent.toString()} />
            <Metric label="До решения" value={progress.decisionReady ? 'ready' : `${progress.daysLeft} дн.`} />
          </div>
        </div>

        <div className="relative overflow-hidden border border-white/10 bg-[#05070a] p-6 shadow-2xl shadow-black/30 md:p-8">
          <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-cyan-data via-amber-industrial to-transparent" />
          <div className="flex h-full flex-col gap-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-mono uppercase tracking-[0.24em] text-white/35">Product preview</p>
                <h2 className="mt-3 text-2xl font-bold">Отчет перед откликом</h2>
              </div>
              <div className="text-right font-mono text-xs uppercase tracking-[0.16em] text-white/42">
                local-only
              </div>
            </div>

            <div className="grid gap-5">
              <div className="border border-white/10 bg-white/[0.035] p-5">
                <div className="flex items-center gap-4">
                  <div className="grid h-20 w-20 shrink-0 place-items-center border border-cyan-data/30 bg-cyan-data/10 text-cyan-data">
                    <Camera className="h-8 w-8" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-sm font-bold">Фото профиля</span>
                      <span className="font-mono text-xs text-cyan-data">76/100</span>
                    </div>
                    <ScoreBar value={76} color="cyan" />
                    <p className="mt-3 text-sm leading-6 text-white/56">
                      Лицо видно, фон отвлекает. Лучше нейтральный светлый фон и кадрирование до плеч.
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <ReportBlock
                  title="Резюме"
                  score="64/100"
                  items={['Заголовок слишком общий', 'Опыт нужно связать с вакансией', 'Добавить измеримые результаты']}
                />
                <ReportBlock
                  title="Отклик"
                  score="81/100"
                  items={['Письмо короткое', 'Есть совпадение по требованиям', 'Нужен сильный первый абзац']}
                />
              </div>

              <div className="border border-amber-industrial/20 bg-amber-industrial/[0.06] p-5">
                <p className="text-xs font-mono uppercase tracking-[0.22em] text-amber-industrial">Cover letter snippet</p>
                <p className="mt-3 text-sm leading-7 text-white/68">
                  "Здравствуйте. Откликаюсь на вакансию, потому что мой опыт в клиентских процессах
                  совпадает с вашими требованиями по CRM, коммуникации и отчетности..."
                </p>
              </div>
            </div>

            <div className="mt-auto grid grid-cols-1 gap-3 border-t border-white/10 pt-5 text-sm text-white/58 md:grid-cols-3">
              <ProofItem text="Без логина hh.ru" />
              <ProofItem text="Без автооткликов" />
              <ProofItem text="Данные локально" />
            </div>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-8 xl:grid-cols-[0.9fr_1.1fr]">
        <form
          id="hh-concierge-form"
          onSubmit={submitLead}
          className="border border-white/10 bg-white/[0.035] p-6 md:p-8"
        >
          <div className="mb-7 flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-mono uppercase tracking-[0.24em] text-cyan-data">Concierge intake</p>
              <h2 className="mt-3 text-3xl font-bold">Зафиксировать intent</h2>
            </div>
            <Mail className="h-6 w-6 text-white/35" />
          </div>

          <div className="grid gap-4">
            <Field label="Контакт">
              <input
                required
                value={form.contact}
                onChange={(event) => updateForm('contact', event.target.value)}
                placeholder="email или Telegram"
                className="booster-input"
              />
            </Field>
            <Field label="Роль / профессия">
              <input
                required
                value={form.role}
                onChange={(event) => updateForm('role', event.target.value)}
                placeholder="например, менеджер продаж"
                className="booster-input"
              />
            </Field>
            <div className="grid gap-4 md:grid-cols-2">
              <Field label="Оффер">
                <select
                  value={form.offer}
                  onChange={(event) => {
                    const nextOffer = event.target.value;
                    if (isOfferId(nextOffer)) {
                      updateForm('offer', nextOffer);
                      setSelectedOffer(nextOffer);
                    }
                  }}
                  className="booster-input"
                >
                  {offers.map((offer) => (
                    <option key={offer.id} value={offer.id}>
                      {offer.title} - {currencyFormatter.format(offer.price)}
                    </option>
                  ))}
                </select>
              </Field>
              <Field label="Готовность платить">
                <select
                  value={form.intent}
                  onChange={(event) => {
                    const nextIntent = event.target.value;
                    if (isPaymentIntent(nextIntent)) updateForm('intent', nextIntent);
                  }}
                  className="booster-input"
                >
                  {Object.entries(intentLabels).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </Field>
            </div>
            <Field label="Канал">
              <select
                value={form.channel}
                onChange={(event) => updateForm('channel', event.target.value)}
                className="booster-input"
              >
                {channelLabels.map((channel) => (
                  <option key={channel} value={channel}>
                    {channel}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Заметки">
              <textarea
                value={form.notes}
                onChange={(event) => updateForm('notes', event.target.value)}
                placeholder="что именно зацепило, цена, возражение, профессия"
                className="booster-input min-h-28 resize-y"
              />
            </Field>
          </div>

          {savedNotice && (
            <div className="mt-5 border border-green-400/20 bg-green-400/10 px-4 py-3 text-sm text-green-200">
              {savedNotice}
            </div>
          )}

          <button
            type="submit"
            className="mt-6 inline-flex h-12 w-full items-center justify-center gap-2 bg-amber-industrial px-5 text-sm font-bold uppercase tracking-[0.12em] text-black transition-colors hover:bg-white"
          >
            Зафиксировать заявку
            <ArrowRight className="h-4 w-4" />
          </button>

          <p className="mt-4 text-xs leading-5 text-white/42">
            Форма пишет только в localStorage этого браузера. Для реального запуска нужен отдельный privacy/delete policy.
          </p>
        </form>

        <div className="space-y-8">
          <section className="border border-white/10 bg-white/[0.035] p-6 md:p-8">
            <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs font-mono uppercase tracking-[0.24em] text-cyan-data">Paid intent by offer</p>
                <h2 className="mt-3 text-3xl font-bold">Сравнение офферов</h2>
              </div>
              <div className="flex gap-2">
                <button type="button" onClick={exportJson} className="booster-tool-button">
                  <Download className="h-4 w-4" />
                  JSON
                </button>
                <button type="button" onClick={exportCsv} className="booster-tool-button">
                  <Download className="h-4 w-4" />
                  CSV
                </button>
                <button type="button" onClick={() => void importServerLeads()} className="booster-tool-button">
                  <Download className="h-4 w-4" />
                  Сервер
                </button>
                <button type="button" onClick={clearLeads} className="booster-tool-button">
                  <Trash2 className="h-4 w-4" />
                  Очистить
                </button>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {metrics.byOffer.map((offerMetric) => (
                <div key={offerMetric.id} className="border border-white/10 bg-black/20 p-5">
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-bold">{offerMetric.title}</span>
                    <span className="font-mono text-xs text-cyan-data">{offerMetric.rate}%</span>
                  </div>
                  <ScoreBar value={offerMetric.rate} color={offerMetric.id === 'response' ? 'amber' : 'cyan'} />
                  <div className="mt-4 grid grid-cols-2 gap-3 text-xs font-mono uppercase tracking-[0.12em] text-white/48">
                    <span>leads {offerMetric.leads}</span>
                    <span>paid {offerMetric.paidIntent}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 border border-cyan-data/20 bg-cyan-data/[0.06] p-5 text-sm leading-7 text-white/68">
              Текущий лидер: <span className="font-bold text-white">{metrics.winner.title}</span>.
              {progress.decisionReady
                ? ' Decision gate пройден: можно выбирать главный оффер по exported JSON.'
                : ' Решение не принимаем, пока не прошли 14 дней и минимальные пороги.'}
            </div>
          </section>

          <section className="border border-white/10 bg-white/[0.035] p-6 md:p-8">
            <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs font-mono uppercase tracking-[0.24em] text-cyan-data">Ежедневный учет</p>
                <h2 className="mt-3 text-3xl font-bold">Ежедневный темп</h2>
              </div>
              <span className="font-mono text-xs uppercase tracking-[0.16em] text-white/42">
                {dailyMetrics.daysAvailable} дн. доступно
              </span>
            </div>

            <div className="grid gap-4 md:grid-cols-4">
              <Metric label="Сегодня лидов" value={dailyMetrics.today.leads.toString()} />
              <Metric label="Сегодня paid" value={dailyMetrics.today.paidIntent.toString()} />
              <Metric label="Средний темп" value={`${formatDecimal(dailyMetrics.averageLeadsPerActiveDay)}/день`} />
              <Metric
                label="Нужно в день"
                value={`${formatDecimal(dailyMetrics.requiredLeadsPerRemainingDay)} / ${formatDecimal(
                  dailyMetrics.requiredPaidPerRemainingDay,
                )}`}
              />
            </div>

            <div className="mt-5 overflow-x-auto border border-white/10 bg-black/20">
              <table className="w-full min-w-[560px] text-left text-sm">
                <thead className="border-b border-white/10 text-xs font-mono uppercase tracking-[0.14em] text-white/38">
                  <tr>
                    <th className="px-4 py-3">Дата</th>
                    <th className="px-4 py-3">Лиды</th>
                    <th className="px-4 py-3">Paid</th>
                    <th className="px-4 py-3">Аватарка</th>
                    <th className="px-4 py-3">Аудит</th>
                    <th className="px-4 py-3">Отклик</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/10 text-white/62">
                  {dailyMetrics.byDay.length ? (
                    dailyMetrics.byDay.slice(0, 7).map((day) => (
                      <tr key={day.date}>
                        <td className="px-4 py-3 font-mono text-white/78">{day.date}</td>
                        <td className="px-4 py-3">{day.leads}</td>
                        <td className="px-4 py-3 text-cyan-data">{day.paidIntent}</td>
                        <td className="px-4 py-3">{day.avatar}</td>
                        <td className="px-4 py-3">{day.audit}</td>
                        <td className="px-4 py-3">{day.response}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td className="px-4 py-5 text-white/45" colSpan={6}>
                        Дневная таблица появится после первой реальной заявки.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          <section className="border border-white/10 bg-white/[0.035] p-6 md:p-8">
            <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs font-mono uppercase tracking-[0.24em] text-cyan-data">Запуск теста</p>
                <h2 className="mt-3 text-3xl font-bold">Ссылки и тексты</h2>
              </div>
              <button type="button" onClick={() => void copyText(publicBaseUrl, 'публичная форма')} className="booster-tool-button">
                <Copy className="h-4 w-4" />
                База
              </button>
            </div>

            <div
              className={`mb-5 border p-4 ${
                usingLocalPublicBase
                  ? 'border-red-400/30 bg-red-400/[0.08]'
                  : 'border-cyan-data/20 bg-cyan-data/[0.06]'
              }`}
            >
              <div className="grid gap-3 md:grid-cols-[1fr_auto] md:items-end">
                <label className="grid gap-2">
                  <span className="font-mono text-xs uppercase tracking-[0.18em] text-white/42">Public host для candidate links</span>
                  <input
                    value={publicBaseOverride}
                    onChange={(event) => setPublicBaseOverride(event.target.value)}
                    onBlur={(event) => savePublicBaseOverride(event.target.value)}
                    placeholder="https://PUBLIC_HOST"
                    className="w-full border border-white/10 bg-black/35 px-3 py-2 font-mono text-sm text-white outline-none transition-colors placeholder:text-white/28 focus:border-cyan-data"
                  />
                </label>
                <div className="flex gap-2">
                  <button type="button" onClick={() => savePublicBaseOverride(publicBaseOverride)} className="booster-tool-button">
                    <CheckCircle2 className="h-4 w-4" />
                    Host
                  </button>
                  <button type="button" onClick={() => savePublicBaseOverride('')} className="booster-tool-button">
                    <RotateCcw className="h-4 w-4" />
                    Сброс
                  </button>
                </div>
              </div>
              <p className="mt-3 break-all text-sm leading-6 text-white/54">
                Сейчас ссылки строятся от: <span className="font-mono text-white/72">{publicBaseUrl}</span>
              </p>
              {usingLocalPublicBase ? (
                <p className="mt-2 text-sm leading-6 text-red-200">
                  Это локальный host. Не отправляй такие ссылки кандидатам.
                </p>
              ) : null}
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              {launchLinks.map((item) => (
                <div key={item.channel} className="border border-white/10 bg-black/20 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-bold">{item.channel}</span>
                    <button
                      type="button"
                      onClick={() => void copyText(item.url, item.channel)}
                      className="inline-flex h-8 w-8 items-center justify-center border border-white/10 text-white/55 transition-colors hover:border-cyan-data hover:text-cyan-data"
                      aria-label={`Скопировать ссылку ${item.channel}`}
                    >
                      <Copy className="h-4 w-4" />
                    </button>
                  </div>
                  <div className="mt-3 break-all font-mono text-xs leading-5 text-white/45">{item.url}</div>
                </div>
              ))}
            </div>

            <div className="mt-5 border border-amber-industrial/20 bg-amber-industrial/[0.05] p-4">
              <div className="mb-3 flex items-center justify-between gap-3">
                <h3 className="font-bold">Прямые ссылки на офферы</h3>
                <span className="font-mono text-xs uppercase tracking-[0.14em] text-white/42">канал + оффер</span>
              </div>
              <div className="grid max-h-[360px] gap-2 overflow-y-auto pr-1 md:grid-cols-2">
                {offerLaunchLinks.map((item) => (
                  <div key={item.key} className="border border-white/10 bg-black/20 p-3">
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-sm font-semibold">
                        {item.offer} / {item.channel}
                      </span>
                      <button
                        type="button"
                        onClick={() => void copyText(item.url, `${item.offer} ${item.channel}`)}
                        className="inline-flex h-8 w-8 items-center justify-center border border-white/10 text-white/55 transition-colors hover:border-cyan-data hover:text-cyan-data"
                        aria-label={`Скопировать ссылку ${item.offer} ${item.channel}`}
                      >
                        <Copy className="h-4 w-4" />
                      </button>
                    </div>
                    <div className="mt-2 break-all font-mono text-xs leading-5 text-white/45">{item.url}</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-5 grid gap-3">
              {outreachTexts.map((item) => (
                <div key={item.title} className="border border-white/10 bg-black/20 p-4">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <h3 className="font-bold">{item.title}</h3>
                    <button type="button" onClick={() => void copyText(item.text, item.title)} className="booster-tool-button">
                      <Copy className="h-4 w-4" />
                      Текст
                    </button>
                  </div>
                  <pre className="whitespace-pre-wrap break-words font-sans text-sm leading-6 text-white/56">{item.text}</pre>
                </div>
              ))}
            </div>
          </section>

          <section className="border border-white/10 bg-[#07090d]/80 p-6 md:p-8">
            <div className="mb-6 flex items-center gap-3">
              <ClipboardCheck className="h-5 w-5 text-amber-industrial" />
              <h2 className="text-2xl font-bold">План на 14 дней</h2>
            </div>
            <div className="grid gap-3">
              <TimelineItem day="1-2" active={progress.currentDay <= 2} text="Запустить страницу и вручную раздать ссылку в карьерных чатах." />
              <TimelineItem day="3-7" active={progress.currentDay >= 3 && progress.currentDay <= 7} text="Собирать заявки, возражения, профессии и цену, не обещая результат по приглашениям." />
              <TimelineItem day="8-12" active={progress.currentDay >= 8 && progress.currentDay <= 12} text="Сделать 10-15 ручных concierge-разборов и сравнить реакцию на три оффера." />
              <TimelineItem day="13-14" active={progress.currentDay >= 13} text="Экспортировать JSON, посчитать paid intent и выбрать главный оффер." />
            </div>
          </section>

          <section className="border border-amber-industrial/20 bg-amber-industrial/[0.055] p-6 md:p-8">
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <p className="font-mono text-xs uppercase tracking-[0.2em] text-amber-industrial">Concierge: следующие действия</p>
                <h2 className="mt-2 text-2xl font-bold">Кому писать первым</h2>
              </div>
              <span className="font-mono text-xs uppercase tracking-[0.18em] text-white/38">{conciergeActions.length} открыто</span>
            </div>
            {conciergeActions.length ? (
              <div className="space-y-3">
                {conciergeActions.map((item) => {
                  const offer = offerById(item.lead.offer);
                  return (
                    <div key={item.lead.id} className="border border-white/10 bg-black/25 p-4">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="border border-amber-industrial/40 bg-amber-industrial/10 px-2 py-1 font-mono text-xs font-bold text-amber-industrial">
                              {item.priority}
                            </span>
                            <span className="font-bold">{item.lead.role || 'Роль не указана'}</span>
                            <span className="text-sm text-white/45">{offer.title}</span>
                          </div>
                          <p className="mt-2 break-words text-sm leading-6 text-white/52">{item.lead.contact || 'Контакт не указан'}</p>
                        </div>
                        <button
                          type="button"
                          onClick={() => void copyText(item.message, `сообщение ${item.lead.id}`)}
                          className="booster-tool-button"
                        >
                          <Copy className="h-4 w-4" />
                          Сообщение
                        </button>
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {item.missingInputs.map((input) => (
                          <span key={input} className="border border-white/10 bg-white/[0.04] px-2 py-1 text-xs text-white/50">
                            нужен {input}
                          </span>
                        ))}
                      </div>
                      <p className="mt-3 break-words text-sm leading-6 text-white/58">{item.message}</p>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="border border-white/10 bg-black/20 p-5 text-sm leading-7 text-white/50">
                Пока нет открытых ready или maybe лидов. После первых заявок здесь появятся приоритет, текст сообщения и недостающие входные данные.
              </div>
            )}
          </section>

          <section className="border border-white/10 bg-white/[0.035] p-6 md:p-8">
            <div className="mb-5 flex items-center justify-between gap-4">
              <h2 className="text-2xl font-bold">Последние заявки</h2>
              <span className="font-mono text-xs uppercase tracking-[0.18em] text-white/38">{leads.length} total</span>
            </div>
            {leads.length ? (
              <div className="space-y-3">
                {leads.slice(0, 6).map((lead) => (
                  <div key={lead.id} className="grid gap-3 border border-white/10 bg-black/20 p-4 md:grid-cols-[1fr_auto]">
                    <div>
                      <p className="font-bold">{lead.role}</p>
                      <p className="mt-1 text-sm text-white/50">{lead.contact}</p>
                      {lead.notes && <p className="mt-2 text-sm leading-6 text-white/48">{lead.notes}</p>}
                    </div>
                    <div className="text-left font-mono text-xs uppercase tracking-[0.12em] text-white/45 md:text-right">
                      <div>{offers.find((offer) => offer.id === lead.offer)?.title}</div>
                      <div className="mt-1 text-cyan-data">{intentLabels[lead.intent]}</div>
                      <div className="mt-1">{new Date(lead.createdAt).toLocaleDateString('ru-RU')}</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="border border-white/10 bg-black/20 p-5 text-sm leading-7 text-white/50">
                Пока нет заявок. Заполни форму слева после первого реального контакта с пользователем.
              </div>
            )}
          </section>
        </div>
      </section>

      <section className="grid gap-4 border border-white/10 bg-black/25 p-6 text-sm leading-7 text-white/56 md:grid-cols-3 md:p-8">
        <div>
          <h3 className="mb-2 font-bold text-white">Что считаем успехом</h3>
          <p>14 дней, 30+ заявок, 10+ strong paid intent, 2+ канала, 5+ ролей, минимум по каждому офферу и явный победитель.</p>
        </div>
        <div>
          <h3 className="mb-2 font-bold text-white">Что не делаем</h3>
          <p>Не логинимся в hh.ru, не скрейпим, не автооткликаемся, не храним резюме и фото в этом прототипе.</p>
        </div>
        <div>
          <h3 className="mb-2 font-bold text-white">Решение после теста</h3>
          <p>Avatar-only оставляем как лид-магнит, если paid intent ниже full audit или response pack.</p>
        </div>
      </section>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="border border-white/10 bg-black/20 p-4">
      <div className="font-mono text-xs uppercase tracking-[0.18em] text-white/38">{label}</div>
      <div className="mt-2 text-3xl font-black">{value}</div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="grid gap-2">
      <span className="font-mono text-xs uppercase tracking-[0.18em] text-white/45">{label}</span>
      {children}
    </label>
  );
}

function GatePill({
  label,
  value,
  target,
  ready,
}: {
  label: string;
  value: number;
  target: number;
  ready: boolean;
}) {
  return (
    <div className={`border p-3 ${ready ? 'border-green-400/25 bg-green-400/10' : 'border-white/10 bg-black/20'}`}>
      <div className="font-mono text-[10px] uppercase tracking-[0.16em] text-white/42">{label}</div>
      <div className="mt-2 text-xl font-black">
        {value}/{target}
      </div>
    </div>
  );
}

function ScoreBar({ value, color }: { value: number; color: 'amber' | 'cyan' }) {
  const clampedValue = Math.max(0, Math.min(100, value));
  return (
    <div className="mt-3 h-2 overflow-hidden bg-white/10">
      <div
        className={color === 'amber' ? 'h-full bg-amber-industrial' : 'h-full bg-cyan-data'}
        style={{ width: `${clampedValue}%` }}
      />
    </div>
  );
}

function ReportBlock({ title, score, items }: { title: string; score: string; items: string[] }) {
  return (
    <div className="border border-white/10 bg-white/[0.035] p-5">
      <div className="flex items-center justify-between gap-3">
        <h3 className="font-bold">{title}</h3>
        <span className="font-mono text-xs text-amber-industrial">{score}</span>
      </div>
      <div className="mt-4 space-y-3">
        {items.map((item) => (
          <div key={item} className="flex gap-3 text-sm leading-6 text-white/58">
            <CheckCircle2 className="mt-1 h-4 w-4 shrink-0 text-cyan-data" />
            <span>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ProofItem({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-2">
      <ShieldCheck className="h-4 w-4 text-cyan-data" />
      <span>{text}</span>
    </div>
  );
}

function TimelineItem({ day, text, active = false }: { day: string; text: string; active?: boolean }) {
  return (
    <div className={`grid grid-cols-[72px_1fr] gap-4 border p-4 ${active ? 'border-amber-industrial/45 bg-amber-industrial/[0.07]' : 'border-white/10 bg-black/20'}`}>
      <div className="font-mono text-xs uppercase tracking-[0.12em] text-amber-industrial">День {day}</div>
      <div className="text-sm leading-6 text-white/60">{text}</div>
    </div>
  );
}
