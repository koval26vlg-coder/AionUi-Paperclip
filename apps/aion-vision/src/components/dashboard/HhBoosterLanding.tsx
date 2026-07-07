import { useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import { ArrowRight, BriefcaseBusiness, Camera, CheckCircle2, FileSearch, ShieldCheck } from 'lucide-react';

type OfferId = 'avatar' | 'audit' | 'response';
type PaymentIntent = 'ready' | 'maybe' | 'not_now';

interface Offer {
  id: OfferId;
  title: string;
  price: number;
  subtitle: string;
  result: string;
  items: string[];
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
type LeadPayload = BoosterLead & { consentAccepted: boolean };

const STORAGE_KEY = 'aion.hhResumeBooster.leads.v1';

const offers: Offer[] = [
  {
    id: 'avatar',
    title: 'Аватарка',
    price: 199,
    subtitle: 'Фото профиля для hh.ru без перегруза и лишней ретуши.',
    result: 'Понять, мешает ли первое впечатление от фото.',
    items: ['Оценка фото', 'Совет по фону и кадру', 'Рекомендация делового стиля'],
  },
  {
    id: 'audit',
    title: 'Аудит резюме',
    price: 399,
    subtitle: 'Фото, заголовок, опыт и блок о себе перед откликами.',
    result: 'Понять, где резюме теряет внимание рекрутера.',
    items: ['Score профиля', '3 главные правки', 'Вариант сильного заголовка'],
  },
  {
    id: 'response',
    title: 'Отклик под вакансию',
    price: 799,
    subtitle: 'Разбор конкретной вакансии, резюме и короткого письма.',
    result: 'Собрать аккуратный отклик под одну реальную вакансию.',
    items: ['Fit под вакансию', 'Черновик письма', 'Чеклист перед отправкой'],
  },
];

const intentLabels: Record<PaymentIntent, string> = {
  ready: 'Готов оплатить',
  maybe: 'Интересно, хочу детали',
  not_now: 'Пока не готов платить',
};

const channelLabels = ['Telegram', 'VK', 'hh.ru', 'Авито Работа', 'Рекомендация', 'Другое'];

const currencyFormatter = new Intl.NumberFormat('ru-RU', {
  style: 'currency',
  currency: 'RUB',
  maximumFractionDigits: 0,
});

function initialChannel() {
  if (typeof window === 'undefined') return 'Telegram';
  const query = window.location.hash.split('?')[1] ?? '';
  const params = new URLSearchParams(query);
  const raw = params.get('channel') ?? params.get('utm_source') ?? '';
  const normalized = raw.trim().toLowerCase();
  const match = channelLabels.find((channel) => channel.toLowerCase() === normalized);
  return match ?? 'Telegram';
}

function initialOffer(): OfferId {
  if (typeof window === 'undefined') return 'audit';
  const query = window.location.hash.split('?')[1] ?? '';
  const params = new URLSearchParams(query);
  const raw = (params.get('offer') ?? '').trim();
  return isOfferId(raw) ? raw : 'audit';
}

function emptyForm(): LeadForm {
  return {
    offer: initialOffer(),
    contact: '',
    role: '',
    intent: 'maybe',
    channel: initialChannel(),
    notes: '',
  };
}

function isOfferId(value: string): value is OfferId {
  return value === 'avatar' || value === 'audit' || value === 'response';
}

function isPaymentIntent(value: string): value is PaymentIntent {
  return value === 'ready' || value === 'maybe' || value === 'not_now';
}

function readStoredLeads(): BoosterLead[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function randomId() {
  return typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `lead-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

async function submitToServer(lead: BoosterLead) {
  if (import.meta.env.DEV) throw new Error('server intake is disabled in Vite dev mode');
  const response = await fetch('/api/hh-booster/leads', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(lead),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return (await response.json()) as { ok?: boolean; lead?: BoosterLead };
}

export default function HhBoosterLanding() {
  const [form, setForm] = useState<LeadForm>(() => emptyForm());
  const [consentAccepted, setConsentAccepted] = useState(false);
  const [selectedOffer, setSelectedOffer] = useState<OfferId>(() => initialOffer());
  const [status, setStatus] = useState<'idle' | 'saving' | 'saved' | 'local' | 'error'>('idle');

  const selected = useMemo(
    () => offers.find((offer) => offer.id === selectedOffer) ?? offers[1],
    [selectedOffer],
  );

  const updateForm = <Key extends keyof LeadForm>(key: Key, value: LeadForm[Key]) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const pickOffer = (offerId: OfferId) => {
    setSelectedOffer(offerId);
    updateForm('offer', offerId);
    document.getElementById('hh-public-intake')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const submitLead = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setStatus('saving');
    const lead: BoosterLead = {
      ...form,
      id: randomId(),
      createdAt: new Date().toISOString(),
      notes: `[public landing] ${form.notes}`.trim(),
    };
    const payload: LeadPayload = { ...lead, consentAccepted };

    try {
      const result = await submitToServer(payload);
      mirrorLead(result.lead ?? lead);
      setStatus('saved');
    } catch {
      mirrorLead(lead);
      setStatus('local');
    }
    setForm({ ...emptyForm(), offer: selectedOffer });
    setConsentAccepted(false);
  };

  const mirrorLead = (lead: BoosterLead) => {
    const current = readStoredLeads();
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify([lead, ...current]));
  };

  return (
    <main className="min-h-screen bg-[#07090d] text-white">
      <section className="mx-auto grid min-h-screen max-w-7xl grid-cols-1 gap-10 px-5 py-8 md:px-8 lg:grid-cols-[1.05fr_0.95fr] lg:py-12">
        <div className="flex flex-col justify-between gap-8">
          <div className="space-y-8">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="inline-flex items-center gap-3 border border-cyan-data/25 bg-cyan-data/10 px-3 py-2 text-xs font-mono uppercase tracking-[0.18em] text-cyan-data">
                <ShieldCheck className="h-4 w-4" />
                Тест HH Resume Booster
              </div>
              <a href="#hh-booster" className="text-xs font-mono uppercase tracking-[0.18em] text-white/45 hover:text-white">
                Панель оператора
              </a>
            </div>

            <div className="max-w-3xl space-y-6">
              <h1 className="text-4xl font-black leading-[0.94] tracking-normal md:text-6xl">
                Проверка резюме и отклика перед hh.ru
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-white/64 md:text-xl">
                Выберите формат, за который вы реально были бы готовы заплатить. Я вручную посмотрю ваш кейс и скажу,
                что сильнее мешает первому впечатлению: фото, резюме или сам отклик.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {offers.map((offer) => {
                const active = selectedOffer === offer.id;
                return (
                  <button
                    key={offer.id}
                    type="button"
                    onClick={() => pickOffer(offer.id)}
                    className={`group flex min-h-[260px] flex-col justify-between border p-5 text-left transition-colors ${
                      active
                        ? 'border-amber-industrial bg-amber-industrial text-black'
                        : 'border-white/10 bg-white/[0.035] hover:border-cyan-data/50 hover:bg-white/[0.06]'
                    }`}
                  >
                    <div className="space-y-4">
                      <div className="flex items-center justify-between gap-4">
                        <OfferIcon offer={offer.id} active={active} />
                        <span className="font-mono text-sm font-black">{currencyFormatter.format(offer.price)}</span>
                      </div>
                      <div>
                        <h2 className="text-2xl font-bold">{offer.title}</h2>
                        <p className={`mt-3 text-sm leading-6 ${active ? 'text-black/70' : 'text-white/58'}`}>
                          {offer.subtitle}
                        </p>
                      </div>
                    </div>
                    <div className="pt-5 text-sm font-semibold leading-6">{offer.result}</div>
                  </button>
                );
              })}
            </div>

            <div className="grid gap-3 text-sm leading-6 text-white/58 md:grid-cols-3">
              <Proof text="Без входа в hh.ru" />
              <Proof text="Без обещаний приглашений" />
              <Proof text="Без загрузки фото в форму" />
            </div>
          </div>

          <div className="border-t border-white/10 pt-6 text-sm leading-7 text-white/48">
            Это concierge-тест спроса. Пока услуга выполняется вручную, а оплата фиксируется как намерение, чтобы понять,
            какой формат нужен людям сильнее.
          </div>
        </div>

        <aside className="border border-white/10 bg-white/[0.035] p-5 shadow-2xl shadow-black/35 md:p-8">
          <div className="mb-7 space-y-3">
            <p className="text-xs font-mono uppercase tracking-[0.24em] text-cyan-data">Заявка на ручной разбор</p>
            <h2 className="text-3xl font-bold">Что проверить?</h2>
            <p className="text-sm leading-7 text-white/55">
              Сейчас выбран формат: <span className="font-bold text-white">{selected.title}</span>.
            </p>
          </div>

          <form id="hh-public-intake" onSubmit={submitLead} className="grid gap-4">
            <Field label="Контакт">
              <input
                required
                value={form.contact}
                onChange={(event) => updateForm('contact', event.target.value)}
                placeholder="Telegram или email"
                className="booster-input"
              />
            </Field>

            <Field label="Профессия">
              <input
                required
                value={form.role}
                onChange={(event) => updateForm('role', event.target.value)}
                placeholder="например, менеджер продаж"
                className="booster-input"
              />
            </Field>

            <Field label="Формат">
              <select
                value={form.offer}
                onChange={(event) => {
                  if (isOfferId(event.target.value)) {
                    setSelectedOffer(event.target.value);
                    updateForm('offer', event.target.value);
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
                  if (isPaymentIntent(event.target.value)) updateForm('intent', event.target.value);
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

            <Field label="Контекст">
              <textarea
                value={form.notes}
                onChange={(event) => updateForm('notes', event.target.value)}
                placeholder="какую работу ищете, что не получается, есть ли конкретная вакансия"
                className="booster-input min-h-28 resize-y"
              />
            </Field>

            <label className="flex items-start gap-3 border border-white/10 bg-black/20 p-4 text-sm leading-6 text-white/58">
              <input
                required
                type="checkbox"
                checked={consentAccepted}
                onChange={(event) => setConsentAccepted(event.target.checked)}
                className="mt-1 h-4 w-4 accent-amber-industrial"
              />
              <span>
                Согласен оставить контакт и описание ситуации для ручного разбора в рамках теста. Можно попросить удалить
                заявку через тот же контакт, который указан в форме.
              </span>
            </label>

            <button
              type="submit"
              disabled={status === 'saving'}
              className="mt-2 inline-flex h-12 items-center justify-center gap-2 bg-amber-industrial px-5 text-sm font-bold uppercase tracking-[0.12em] text-black transition-colors hover:bg-white disabled:opacity-60"
            >
              {status === 'saving' ? 'Сохраняю' : 'Отправить заявку'}
              <ArrowRight className="h-4 w-4" />
            </button>
          </form>

          <StatusMessage status={status} />

          <div className="mt-8 border border-white/10 bg-black/20 p-5">
            <h3 className="font-bold">Что входит в выбранный формат</h3>
            <div className="mt-4 grid gap-3">
              {selected.items.map((item) => (
                <div key={item} className="flex gap-3 text-sm leading-6 text-white/58">
                  <CheckCircle2 className="mt-1 h-4 w-4 shrink-0 text-cyan-data" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>
        </aside>
      </section>
    </main>
  );
}

function OfferIcon({ offer, active }: { offer: OfferId; active: boolean }) {
  const className = active ? 'h-6 w-6 text-black' : 'h-6 w-6 text-cyan-data';
  const icon =
    offer === 'avatar' ? (
      <Camera className={className} />
    ) : offer === 'audit' ? (
      <FileSearch className={className} />
    ) : (
      <BriefcaseBusiness className={className} />
    );
  return <div className="grid h-12 w-12 place-items-center border border-current/20 bg-black/10">{icon}</div>;
}

function Proof({ text }: { text: string }) {
  return (
    <div className="flex items-center gap-2 border border-white/10 bg-black/20 px-3 py-2">
      <ShieldCheck className="h-4 w-4 text-cyan-data" />
      <span>{text}</span>
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

function StatusMessage({ status }: { status: 'idle' | 'saving' | 'saved' | 'local' | 'error' }) {
  if (status === 'idle' || status === 'saving' || status === 'error') return null;
  const isServer = status === 'saved';
  return (
    <div
      className={`mt-5 border px-4 py-3 text-sm leading-6 ${
        isServer ? 'border-green-400/20 bg-green-400/10 text-green-100' : 'border-amber-industrial/25 bg-amber-industrial/10 text-amber-100'
      }`}
    >
      {isServer
        ? 'Заявка сохранена. Я свяжусь с вами по указанному контакту.'
        : 'Заявка сохранена в этом браузере. Для внешней ссылки нужен запуск Aion Vision через серверный режим.'}
    </div>
  );
}
