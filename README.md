# MyPro

**MyPro** — открытая модульная платформа для анализа, создания, монтажа, преобразования и проверки цифрового контента.

Главное архитектурное ядро MyPro — не UI и не конкретный видеоредактор. Это **event-sourced, content-addressed среда для проверяемого происхождения контента и решений над ним**.

Монтаж, AI, безопасность и аудит рассматриваются как приложения одного Evidence Core.

## Основной принцип

Контент сначала представляется как проверяемая совокупность данных, наблюдений и происхождения. Затем он может быть интерпретирован алгоритмами, AI или человеком.

Граница решений:

**AI или анализатор предлагает. Core проверяет. Человек или политика принимает решение. Action применяет изменение. Project фиксирует результат.**

Наблюдение не является выводом. Вывод не является приговором. Предложение не является изменением.

## Foundation v0.2

В репозитории уже заложены:

- формальная онтология Asset, Observation, Interpretation, Finding, Hypothesis, Proposal, Decision, Action, Revision, Invariant и Policy;
- schema-first описание проекта, наблюдений, предложений и capabilities;
- рациональная временная модель с полуоткрытыми интервалами;
- append-only JSONL event log;
- базовая versioned Observation model;
- provenance и content-addressed архитектурные принципы;
- каталог архитектурных инвариантов;
- границы plugin sandbox и capability security;
- документация по interoperability, threat model и privacy.

Следующий практический слой — Media Probe, MediaManifest, атомарное сохранение проекта и проверяемое резервное копирование.

## Архитектура

```text
MyPro
├── Media
├── Analysis
├── Evidence
├── Project
├── Montage
├── AI
├── Security
├── Runtime
└── Integrations
```

### Media

Работает с исходными файлами, идентичностью, техническими метаданными, хэшами и proxy.

### Analysis

Производит версионируемые Observation с confidence, uncertainty, status и provenance.

Анализ строится как DAG вычислений, чтобы поддерживать кэширование, инкрементальный пересчёт и обнаружение устаревших результатов.

### Evidence

Связывает исходный Asset, Observation, Interpretation, Finding, Proposal, Decision и Action с их происхождением.

### Project

Проект хранит не только текущее состояние, но и историю изменений. Event log является append-only журналом, snapshots ускоряют восстановление.

### Montage

Каноническая монтажная модель остаётся независимой от UI и конкретного renderer. OpenTimelineIO используется как interchange, а не как скрытый источник истины.

### AI

AI создаёт Proposal. Изменение проекта возможно только через явный policy-controlled путь с фиксацией Decision, Action и Revision.

### Security

Плагины работают по принципу deny by default. Capability описывает техническую возможность, но сама по себе не означает разрешение на конкретное действие.

## Структура

- `spec/` — формальные спецификации;
- `schemas/` — JSON Schema;
- `core/` — доменное ядро;
- `runtime/` — границы исполнения расширений;
- `ai/` — AI proposals и orchestration;
- `integrations/` — FFmpeg, OTIO, C2PA, MLT и другие внешние системы;
- `apps/` — будущие приложения RosEdit;
- `tests/`, `benchmarks/`, `fuzz/` — проверка и измерения;
- `docs/` — архитектурные документы.

## Open-source synthesis

MyPro использует открытые проекты как совместимые зависимости, интеграционные границы и источники архитектурных идей. Код с несовместимыми лицензиями не копируется в MIT-ядро.

Ключевые направления: FFmpeg/FFprobe, OpenTimelineIO, MLT, C2PA и W3C PROV. Практические NLE-проекты могут использоваться как workflow reference без превращения MyPro в скрытый fork.

## Безопасность и обратимость

Проектная модель предусматривает:

- atomic writes;
- schema migrations;
- snapshots;
- проверяемые backups;
- внешние ссылки с прозрачным состоянием;
- provenance;
- capability audit;
- fuzzing медиапарсеров;
- воспроизводимость анализа.

## Agent Protocol Runtime

The current machine-first agent coordination layer is **v0.2**. It provides typed event envelopes, deterministic task state transitions, independent-verification gates, explicit decision and authorization records, idempotent append-only logging, and a strict boundary around GitHub mutation.

The protocol deliberately separates assertion, observation, verification, proposal, authorization and change. Replaying an identical event is a no-op; reusing an event identifier or idempotency key for different content is rejected as a protocol conflict.

## Roadmap

**Phase 0 — Foundation:** Media Probe, MediaManifest, Project Format, Event Log, Backup/Recovery.

**Phase 1 — Evidence:** Analysis DAG, Observation Schema, Provenance, Plugin SDK, Capability Security.

**Phase 2 — Montage:** Montage Model, OTIO interchange, базовый редактор.

**Phase 3 — AI:** Proposal Engine, Policy Engine, Human-in-the-loop, RosEdit.

**Phase 4 — Ecosystem:** Security Analyzer, EthicalAudit, РосЭкшн, RosAction и расширения.

## «Мира» — Epistemic Governance System

В `docs/mira/` и `spec/mira-eel-v0.4.md` зафиксирована формальная ветвь исследований «Миры»: CGPF/UACL/RSL/MCL, MOSL/RIC, EAL, HFTP, ISCL, RIP и EEL. Текущая версия переводит архитектуру в измеримое пространство состояний `(Ω, FΩ, K)` и явно отделяет доказанные свойства от гипотез и непроверенных утверждений.

## Статус

Проект находится на стадии архитектурного основания. Коммерческие параметры, характеристики будущего оборудования, производительность и сроки являются проектными гипотезами, пока не подтверждены прототипами и испытаниями.

## Лицензия

MIT. См. LICENSE.

## Media Perception Observation Profile (MPOP) v0.1

[Спецификация MPOP](spec/media_perception_observation_profile.md) описывает proposed schema profile для измерения длительности видимости объектов и отдельной фиксации результатов задач восприятия и памяти. Профиль использует существующие rational Time Model, versioned Observation, provenance и Analysis DAG. Это спецификация для реализации, а не утверждение о готовом или валидированном анализаторе. Экспозиция объекта не считается доказательством обнаружения, запоминания или причинного медиаэффекта.

## Media Perception Observation Profile — initial implementation

The first typed records and unit tests are now available: [implementation status](spec/media_perception_implementation_status.md), [typed data model](core/analysis/media_perception.py), and [tests](tests/test_media_perception.py). This is an implementation scaffold only; no media decoder, psychometric fitting, or validated human-perception threshold is claimed.

Psychometric fitting prototype: [fit implementation](core/analysis/psychometric_fit.py), [tests](tests/test_psychometric_fit.py), [fitting protocol](spec/psychometric_fitting_protocol.md). The current fitter estimates a logistic curve's midpoint and slope from aggregate binomial counts with fixed guess/lapse rates. It is not validated for real participant data, does not estimate uncertainty, and does not model participant-level effects.

Synthetic validation scaffold: [scripts/validate_psychometric_synthetic.py](scripts/validate_psychometric_synthetic.py). Run `python -m scripts.validate_psychometric_synthetic` from the repository root. This is a generated-data smoke check only, not validation on real viewers.

## Multimodal psychophysiology experiment preparation

Planning protocol: [multimodal psychophysiology experiment protocol v0.1](spec/multimodal_psychophysiology_experiment_protocol.md). It defines candidate sensor channels, event synchronization, calibration and artifact handling, study readiness gates, privacy/consent requirements, and proposed MyPro data entities. It is a planning specification only; no device validation, ethics approval, recruitment or data collection is claimed.

## Экспериментальная аппаратура MyPro × «Синема Катарсис»

[Базовый реестр оборудования и план реализации при нулевом бюджете](spec/experimental_equipment_inventory.md) фиксирует кандидатов (Tobii Pro Fusion / Pupil Labs Neon, Polar H10, синхронизация LSL и условный будущий EEG), ориентировочный бюджет, ограничения, план проверки и условия университетского сотрудничества. Это план, а не заказ или подтверждение характеристик; текущий доступный бюджет указан как €0.

[Пакет для университетского сотрудничества](docs/university_collaboration_proposal.md) описывает цель технического пилота, вклад сторон, требования к лаборатории, этапы проверки синхронизации и этические ограничения. Предложение рассчитано на старт без закупки оборудования автором.