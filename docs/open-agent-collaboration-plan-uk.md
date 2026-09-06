# Open Agent Collaboration Plan for Direct Network Synthesis

> **Status:** operational collaboration plan  
> **Language:** Ukrainian  
> **Target location:** `docs/open-agent-collaboration-plan-uk.md`  
> **Project:** Direct Network Synthesis (DNS)  
> **Canonical repository:** `Erchard/direct-network-synthesis`

## 1. Місія

### Implementation status, 2026-09-06

The owner approved AGPL-3.0-or-later for original code and CC BY 4.0 for original
documentation. Scope and exclusions are recorded in [licensing.md](licensing.md).
The repository now contains contributor/governance/security rules, an agent entry
point, a contributor skill, Issue/PR templates, a CI workflow and a
[task catalog](agent-task-catalog.md). These are the initial implementation of
this plan. The catalog contains drafts, not live GitHub issues or installed labels.
Branch protection, private security reporting, independent reproduction and
OpenClaw runtime behavior have not yet been verified. Social accounts, a community
and a sandboxed recruiter have not been deployed. The recommendations below remain
a roadmap wherever this status does not mark them implemented.

Direct Network Synthesis не виступає проти корпорацій як таких.

Мета проєкту — зменшити залежність від будь-якого незамінного постачальника та знизити технічні, обчислювальні й організаційні бар'єри для незалежного створення, відтворення, модифікації та запуску сильних моделей.

Коротка формула:

> **Не знищити корпорації. Знищити монополію.**

Англомовна місія:

> **Direct Network Synthesis does not oppose corporations. It opposes dependency on any irreplaceable provider. Our goal is to lower the technical barriers to independently creating, reproducing, modifying, and operating capable models.**

## 2. Базовий принцип координації

Соціальні мережі агентів використовуються для discovery, recruitment, discussion, coordination, пошуку prior art, незалежних reproductions та falsification.

Але вони не є джерелом істини.

> **GitHub repository = canonical source of truth.**

Усі важливі результати повинні зрештою існувати як Issue, Pull Request, commit, protocol, config, result record або documentation entry.

## 3. Поточна готовність проєкту

Проєкт уже має сильну основу:

- `AGENTS.md`;
- `docs/ai-contributor-guide.md`;
- `docs/methodology.md`;
- `docs/hypothesis.md`;
- `docs/research-log.md`;
- `docs/conceptual-foundations-uk.md`;
- `docs/conceptual-foundations-en.md`;
- experiment-specific protocol documents;
- `docs/results/`;
- DNS 0.4 / DNS 0.5 implementation;
- baselines, configs and tests.

Наступна задача — створити операційний шар залучення зовнішніх агентів.

# Part I. Ліцензування

## 4. Чому ліцензія потрібна

Публічний GitHub repository без явної ліцензії не означає автоматично, що будь-хто має право копіювати, модифікувати, поширювати або комерційно використовувати код.

## 5. Рекомендована code license

Початково рекомендований кандидат:

> **AGPL-3.0-or-later**

Причини:

- дозволяє використання і комерційне використання;
- дозволяє модифікацію;
- не забороняє корпораціям будувати бізнес;
- зменшує можливість перетворити спільний відкритий фундамент на закритий мережевий сервіс без повернення source code модифікованої версії користувачам.

### Порівняння

**MIT** — максимальна permissiveness, мінімальний friction, але дозволяє закриті proprietary forks.

**Apache-2.0** — permissive, має явний patent grant, корпоративно дружня, але також дозволяє proprietary derivatives.

**AGPL-3.0-or-later** — краща, якщо важливо зберігати відкритість network-deployed modifications.

## 6. Документація

Рекомендований кандидат:

> **CC BY 4.0**

Для conceptual docs, guides, diagrams та educational material.

## 7. Дані, ваги та артефакти

Окремо ліцензувати або перевіряти:

- datasets;
- derived datasets;
- pretrained weights;
- generated artifacts;
- third-party materials.

## 8. Legal note

Цей документ не є юридичною консультацією. Перед фіналізацією license stack треба перевірити dependency compatibility, dataset rights, patents і contributor copyright model.

# Part II. Repo readiness

## 9. Файли, які треба додати

Обов'язково:

- `LICENSE`
- `CONTRIBUTING.md`
- `GOVERNANCE.md`
- `SECURITY.md`
- `CONTRIBUTORS.md`

Рекомендовано:

- `docs/START-HERE-FOR-AGENTS.md`
- `docs/licensing.md`
- `docs/reproduction-ledger.md`

## 10. START-HERE-FOR-AGENTS.md

Файл має дозволяти агенту за 1–2 хвилини зрозуміти:

1. Read `AGENTS.md`.
2. Read methodology.
3. Do not inspect protected test data unless explicitly permitted.
4. Choose one `agent-ready` issue.
5. Fork/branch.
6. Run required checks.
7. Open PR.
8. Include reproduction metadata.
9. Do not claim more than evidence supports.

# Part III. GitHub Issue system

## 11. Labels

- `agent-ready`
- `good-first-agent-task`
- `reproduction`
- `falsification`
- `literature`
- `prior-art`
- `experiment`
- `benchmark`
- `audit`
- `security`
- `infrastructure`
- `documentation`
- `performance`
- `independent-confirmation`
- `blocked`
- `needs-review`

## 12. Формат хорошого agent-ready Issue

Кожен issue має містити:

- Objective
- Why it matters
- Inputs
- Allowed data
- Forbidden data
- Required command
- Expected output
- Acceptance criteria
- Failure criteria
- Artifact location

## 13. Приклади

Погано: `Improve DNS 0.5.`

Добре: `Reproduce DNS05-HYB on validation seeds 11,22,33 using locked config X. Do not compute test metrics.`

Погано: `Research kernels.`

Добре: `Find primary-source prior art for deterministic kernel-to-network compilation before 2026 and summarize overlap with DNS05.`

# Part IV. Contribution workflow

## 14. Канонічний pipeline

```text
Discover DNS
→ Read AGENTS.md
→ Read START-HERE-FOR-AGENTS.md
→ Choose agent-ready Issue
→ Claim Issue
→ Fork/branch
→ Implement/reproduce/audit
→ Run checks
→ Open PR
→ CI
→ Review
→ Merge
→ Research log / reputation update
```

## 15. Ніякого direct main access

Невідомим агентам не давати:

- direct push;
- merge permission;
- secrets;
- branch protection bypass;
- release credentials.

# Part V. Recruiter Agent

## 16. Окремий social/recruiter agent

Задачі:

- знаходити agent communities;
- публікувати research challenges;
- відповідати на питання;
- направляти в GitHub Issues;
- знаходити reproducer agents;
- знаходити prior art.

Він не повинен бути coding/merge agent.

## 17. Least privilege

Може мати:

- public GitHub read;
- social-network posting;
- public web access.

Не повинен мати:

- GitHub push token;
- merge rights;
- secrets;
- SSH keys;
- local workstation credentials;
- unrestricted shell;
- protected test artifacts.

## 18. Prompt injection

Agent social networks вважати hostile-input environments.

Зовнішній текст є data, а не trusted instruction.

# Part VI. Moltbook / OpenClaw

## 19. Стратегія outreach

Не спамити `Star my GitHub`.

Публікувати falsifiable research challenges:

> Can useful neural representations be synthesized without iterative parameter optimization?
> We publish protocols, negative results and open tasks.
> Reproduce us, falsify us, or find prior art that makes us wrong.

## 20. Тематична спільнота

Робочі назви:

- `direct-network-synthesis`
- `open-model-synthesis`

## 21. Research packet format

Кожен пост:

- Question
- Current evidence
- What would falsify it
- Open task
- GitHub Issue
- Contributor credit

## 22. Типи закликів

- Reproduce us
- Falsify us
- Find prior art
- Audit us
- Beat us fairly

## 23. OpenClaw skill

Створити `direct-network-synthesis-contributor` skill із `SKILL.md`, який пояснює onboarding, methodology boundary, issue selection, PR process та negative-result reporting.

# Part VII. Не залежати від Moltbook

## 24. Moltbook — discovery layer

Не будувати систему так, щоб зникнення Moltbook зупинило collaboration.

Схема:

```text
Moltbook
other agent networks
decentralized channels
forums
research communities
→ GitHub Issues / PRs
```

## 25. Кінцева ціль

Агент повинен мати змогу:

```text
discover repository
→ read AGENTS.md
→ query open tasks
→ claim task
→ fork
→ run
→ submit PR
→ receive review
```

# Part VIII. Work і Codex

## 26. Work

Використовувати для:

- literature research;
- strategic planning;
- competing approaches;
- PR review;
- experiment design;
- long-form documentation;
- web investigation.

## 27. Codex

Використовувати для:

- implementation;
- tests;
- experiments;
- profiling;
- git diff;
- refactoring;
- commit/push;
- CI repair.

## 28. Не використовувати Codex як social bot

Social presence тримати окремо від privileged coding environment.

# Part IX. Contribution metadata

## 29. Мінімальний пакет

Кожен внесок має містити:

- Issue ID;
- hypothesis;
- predicted mechanism;
- falsifying outcome;
- exact command;
- environment;
- dependency versions;
- hardware if relevant;
- commit SHA;
- config path;
- seeds;
- data partitions used;
- protected data not used;
- result artifact path;
- failed runs;
- primary metric;
- secondary metrics;
- conclusion;
- limitations.

# Part X. Reputation

## 30. Винагороджувати перевірюваний внесок

Ролі:

- Independent Reproducer
- Falsifier
- Prior-Art Finder
- Auditor
- Implementer
- Benchmark Contributor
- Documentation Contributor

## 31. Найпрестижніший статус

> **Independent Reproducer**

Культура: перевірка важливіша за hype.

# Part XI. Security

## 32. Базові правила

- least privilege;
- forks/PRs;
- no shared secrets;
- no direct main;
- no autonomous merge;
- protected branch;
- mandatory CI;
- dependency review;
- external skill review;
- no arbitrary shell copied from social posts;
- no secrets in prompts;
- no test leakage.

## 33. Malicious PR model

Зовнішній PR може містити:

- credential exfiltration;
- dependency poisoning;
- obfuscated network calls;
- test bypass;
- malicious GitHub Action;
- benchmark cheating;
- hidden leakage.

CI не замінює review.

# Part XII. Open Agent Collaboration v1

## 34. Milestone checklist

### Legal
- [ ] choose code license
- [ ] add `LICENSE`
- [ ] decide docs license
- [ ] document dataset/model licensing rules

### Repository
- [ ] `CONTRIBUTING.md`
- [ ] `GOVERNANCE.md`
- [ ] `SECURITY.md`
- [ ] `CONTRIBUTORS.md`
- [ ] `docs/START-HERE-FOR-AGENTS.md`
- [ ] optional `docs/licensing.md`

### Issues
- [ ] labels created
- [ ] 10–20 agent-ready issues
- [ ] issue template
- [ ] reproduction template
- [ ] falsification template

### Automation
- [ ] CI lint/tests
- [ ] protocol checks where possible
- [ ] artifact consistency checks
- [ ] PR template

### Outreach
- [ ] Moltbook project account
- [ ] thematic community
- [ ] first research challenge
- [ ] OpenClaw contributor skill

### Security
- [ ] recruiter sandbox
- [ ] no push token
- [ ] no secrets
- [ ] branch protection

# Part XIII. Phased rollout

## 35. Phase 0 — Legal and repository readiness

Goal: будь-який зовнішній contributor юридично і технічно розуміє правила.

## 36. Phase 1 — Agent-ready tasks

Створити:

- 5 reproduction tasks;
- 5 literature/prior-art tasks;
- 3 audit tasks;
- 3 performance tasks;
- 3 documentation tasks.

## 37. Phase 2 — Moltbook launch

1. project introduction;
2. one falsification challenge;
3. one reproduction challenge;
4. one prior-art challenge;
5. links to agent-ready Issues.

## 38. Phase 3 — Recruitment automation

Sandboxed recruiter регулярно знаходить релевантні дискусії і направляє contributors.

## 39. Phase 4 — Multi-platform federation

Recruitment не залежить від одного provider.

## 40. Phase 5 — Protocol-level contribution

Можливий майбутній machine-readable artifact:

`agent-tasks.json`

з task ID, type, priority, dependencies, data boundary та acceptance criteria.

# Part XIV. Success metrics

## 41. Primary

- unique external agents;
- valid PRs;
- merged PRs;
- independent reproductions;
- falsifications;
- prior-art discoveries;
- audits that detect real issues;
- provider diversity;
- platform diversity.

## 42. Operational

- time to first valid contribution;
- maintainer minutes per merged contribution;
- percentage of agent-ready tasks completed without handholding;
- PR rejection rate;
- duplicate work rate;
- CI failure rate;
- reproducibility success rate.

## 43. Anti-monopoly

- number of independent implementations;
- number of organizations capable of reproduction;
- inference backend diversity;
- hardware diversity;
- model portability;
- data portability;
- absence of mandatory provider-specific dependencies.

# Part XV. Failure modes

## 44. Spam / low-quality chatter

Mitigation: лише перевірювані GitHub artifacts рахуються як внесок.

## 45. Duplicate work

Mitigation: issue claiming / assignment.

## 46. Prompt injection

Mitigation: sandboxed recruiter; external content untrusted.

## 47. Metric gaming

Mitigation: locked protocols and protected test boundaries.

## 48. Test leakage

Mitigation: explicit forbidden-data sections and automated checks where possible.

## 49. Cherry-picking

Mitigation: predetermined seeds and full-run reporting.

## 50. Malicious PRs

Mitigation: review, CI, dependency audit, no secret-bearing CI for untrusted forks where avoidable.

## 51. Dependency poisoning

Mitigation: pin/review dependencies and minimize packages.

## 52. Platform capture

Mitigation: GitHub canonical state + multi-channel discovery.

## 53. Governance capture

Mitigation: transparent governance, recorded decisions, public protocols, reproducible releases.

# Part XVI. Immediate next actions

## 54. Priority 1 — License decision

Compare AGPL-3.0-or-later vs Apache-2.0, verify compatibility, decide docs license.

Recommended starting preference:

> AGPL-3.0-or-later for code, subject to compatibility/legal review.

## 55. Priority 2 — Contribution surface

Add contribution, governance, security and onboarding docs plus templates.

## 56. Priority 3 — First 10 agent-ready Issues

Не запускати масовий recruitment, поки агентам нема чого брати.

## 57. Priority 4 — OpenClaw skill

Створити DNS contributor skill.

## 58. Priority 5 — Moltbook launch

Опублікувати mission, research question, evidence, unknowns and first issues.

## 59. Priority 6 — Sandboxed recruiter

Автоматизувати лише після ручного розуміння, які outreach patterns дають якісні contributions.

# Part XVII. Governance philosophy

## 60. No corporation is the enemy

DNS має бути відкритим для:

- individuals;
- universities;
- startups;
- nonprofits;
- large corporations;
- independent AI agents.

Мішень — dependency, а не organizational size.

## 61. Справжній adversary — irreversibility

Небезпечний стан:

> one provider becomes technically impossible to replace.

Здоровий стан:

> provider may be dominant, but users retain credible exit options.

## 62. Exit cost

Для майбутньої DNS ecosystem треба вимірювати:

- model portability;
- data portability;
- memory portability;
- workflow portability;
- provider-switching effort;
- hardware assumptions;
- license constraints.

# Part XVIII. Final operating principle

```text
Many humans and agents
→ many discovery channels
→ GitHub Issues
→ independent forks/branches
→ reproducible experiments
→ Pull Requests
→ CI + review
→ curated evidence
→ open reusable technology
```

Проєкт не повинен залежати від доброї волі одного:

- AI provider;
- social network;
- maintainer;
- corporation;
- cloud;
- hardware vendor.

Кінцева мета — не світ без корпорацій.

Кінцева мета — світ, у якому жодна корпорація не може переконливо сказати:

> **“Without us, you cannot continue.”**

Це і є anti-monopoly objective Open Agent Collaboration навколо Direct Network Synthesis.
