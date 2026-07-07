# 2026-06-21 21:04 +03 - Codex - HH Resume Booster one-command launch guard

## Исходный запрос

Продолжить активную цель: подготовить landing/concierge test на 2 недели с тремя офферами (`avatar-only`, `full resume audit`, `vacancy response pack`) и довести практический запуск до безопасного состояния.

## Краткий план

- Проверить текущее состояние HH Resume Booster runtime, experiment state, manifest и public tunnel.
- Верифицировать one-command public launch flow без фактического старта теста.
- Если найден риск преждевременного старта, исправить guard.
- Обновить runbook, текущий контекст и задачи.

## Что было сделано

- Подтянут SML bootstrap по теме HH Resume Booster launch verification.
- Проверен unrelated trading gate: `RUNNING`, поэтому по trading/postprocess действий не выполнялось.
- Подтвержден канонический experiment state path: `apps/aion-vision/data/hh-booster-experiment.json`.
- Проверено, что production server на `http://127.0.0.1:8787` жив, а experiment еще не стартовал: `startedAt=null`, leads `0`, manifest отсутствует.
- Обнаружено, что текущий public localtunnel `https://huge-moons-fail.loca.lt` стал нестабилен: public API вернул `503 Service Unavailable`/timeout.
- Исправлен `apps/aion-vision/scripts/prepare-hh-booster-public-launch.ps1`: теперь `-StartExperiment` перед записью `startedAt` запускает pre-start readiness check через `hh_resume_booster_prelaunch_check.py --json`.
- Новый guard разрешает старт только если единственные fail checks до старта — ожидаемые `experiment_started` и `launch_manifest`; любые failures public HTTP/API/server/data quality блокируют запись таймера.
- Обновлен runbook `docs/experiments/hh-resume-booster-validation.md`.
- Обновлены `docs/current-context.md` и `docs/tasks.md`.
- После фикса guard поднят новый public localtunnel в видимом Windows PowerShell-окне: PID `26992`, URL `https://public-rooms-camp.loca.lt/#hh-booster-public`, лог `apps/aion-vision/data/hh-booster-public-tunnel-20260621-210708.log`.
- Новый public URL прошел `preflight-hh-booster-test.ps1` с `Result: ok`; `hh_resume_booster_prelaunch_check.py` остается ожидаемо `NO-GO` только из-за `experiment_started` и `launch_manifest`.
- `apps/aion-vision/data/hh-booster-publish-kit.md` перегенерирован под новый URL.
- `tools/hh_resume_booster_publish_kit.py` дополнен статусом `Launch status` и разделом `One-command Launch`, чтобы publish kit был самодостаточным launch bundle.

## Измененные файлы

- `apps/aion-vision/scripts/prepare-hh-booster-public-launch.ps1`
- `tools/hh_resume_booster_publish_kit.py`
- `docs/experiments/hh-resume-booster-validation.md`
- `docs/current-context.md`
- `docs/tasks.md`
- `docs/agent-log/2026-06-21-2104-codex-hh-booster-one-command-launch-guard.md`

## Проверки

- `prepare-hh-booster-public-launch.ps1 -PublicBaseUrl https://huge-moons-fail.loca.lt -OperatorBaseUrl http://127.0.0.1:8787 -CheckPublicHttp -StartExperiment -PrintOnly` через Windows PowerShell 5.1: печатает one-command launch и не пишет состояние.
- `prepare-hh-booster-public-launch.ps1 ... -CheckPublicHttp -StartExperiment` на текущем плохом tunnel: вернул `EXIT_CODE=2`, `NO-GO`, `MANIFEST_EXISTS=False`.
- `hh_resume_booster_experiment_state.py --state ...\hh-booster-experiment.json --data ...\hh-booster-leads.jsonl status --json`: `startedAt=null`, `total_leads=0`.
- `hh_resume_booster_prelaunch_check.py --operator-base-url http://127.0.0.1:8787 --public-base-url https://huge-moons-fail.loca.lt --check-public-http --json`: ожидаемый `NO-GO`, public tunnel/API нестабилен, experiment/manifest еще не готовы.
- `python -m py_compile` для затронутых HH tools прошел.
- `start-hh-booster-public-tunnel.ps1 -Port 8787 -LogPath ...hh-booster-public-tunnel-20260621-210708.log` запущен в видимом PowerShell-окне через `Start-Process`, PID `26992`.
- `Invoke-WebRequest https://public-rooms-camp.loca.lt/api/hh-booster/experiment`: HTTP `200`, `startedAt=null`.
- `preflight-hh-booster-test.ps1 -BaseUrl http://127.0.0.1:8787 -PublicBaseUrl https://public-rooms-camp.loca.lt`: `Result: ok`.
- `watch-hh-booster-test.ps1 -OperatorBaseUrl http://127.0.0.1:8787 -PublicBaseUrl https://public-rooms-camp.loca.lt`: `Public URL: ready`, `Started: no`, `Manifest: missing`.
- `python -m py_compile tools/hh_resume_booster_publish_kit.py` прошел.
- `hh_resume_booster_publish_kit.py --public-base-url https://public-rooms-camp.loca.lt --operator-base-url http://127.0.0.1:8787 --write` перегенерировал `apps/aion-vision/data/hh-booster-publish-kit.md`.
- Readback top 40 lines подтвердил `Launch status: ready for guarded start only` и раздел `One-command Launch` с `-CheckPublicHttp -StartExperiment`.

## Риски и ограничения

- Старый public URL `https://huge-moons-fail.loca.lt` нельзя раздавать кандидатам: tunnel нестабилен.
- Актуальный public URL на момент записи: `https://public-rooms-camp.loca.lt/#hh-booster-public`. Это временный localtunnel, перед рассылкой его нужно еще раз проверить preflight/prelaunch.
- 14-дневное окно намеренно не стартовало, чтобы не исказить день 1.
- `hh-booster-launch-manifest.md` не создан, потому что public launch не готов.
- В текущем shell временами не находится `powershell.exe` через PATH; для проверок использован абсолютный путь `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`.

## Что должен проверить следующий агент

- Использовать текущий видимый tunnel `https://public-rooms-camp.loca.lt` только если он еще проходит public preflight; иначе получить новый stable tunnel/domain.
- Запустить public preflight с `-CheckPublicHttp`.
- Если public URL стабилен и оператор готов начинать сбор, выполнить:

```powershell
& "D:\AionUi-Paperclip\apps\aion-vision\scripts\prepare-hh-booster-public-launch.ps1" -PublicBaseUrl "https://public-rooms-camp.loca.lt" -OperatorBaseUrl "http://127.0.0.1:8787" -CheckPublicHttp -StartExperiment
```

- Публиковать candidate links только после `Status: GO`.
