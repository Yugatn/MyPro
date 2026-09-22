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

## Roadmap

**Phase 0 — Foundation:** Media Probe, MediaManifest, Project Format, Event Log, Backup/Recovery.

**Phase 1 — Evidence:** Analysis DAG, Observation Schema, Provenance, Plugin SDK, Capability Security.

**Phase 2 — Montage:** Montage Model, OTIO interchange, базовый редактор.

**Phase 3 — AI:** Proposal Engine, Policy Engine, Human-in-the-loop, RosEdit.

**Phase 4 — Ecosystem:** Security Analyzer, EthicalAudit, РосЭкшн, RosAction и расширения.

## Статус

Проект находится на стадии архитектурного основания. Коммерческие параметры, характеристики будущего оборудования, производительность и сроки являются проектными гипотезами, пока не подтверждены прототипами и испытаниями.

## Лицензия

MIT. См. LICENSE.
