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
this plan. Following the owner's operational-launch instruction, twelve
[live issues and the requested labels](outreach/README.md) are now published;
the limit remains three active claims, not three published backlog entries.
Six outreach packets and a recruiter specification are prepared. The branches/main
API reported protected=false; private security reporting, independent reproduction
and OpenClaw runtime remain unverified. Moltbook browser access was blocked and
Discord was unauthenticated, so no social post, account or recruiter was deployed.
See the [publication log](outreach/targets-and-publication-log.md) for exact targets
and access requirements. The recommendations below remain a roadmap where not
marked implemented; new user-directed launch scope supersedes old rollout ordering.

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
- [x] choose code license: AGPL-3.0-or-later, owner approved
- [x] add `LICENSE`
- [x] decide docs license: CC BY 4.0, owner approved
- [x] document dataset/model licensing scope and exclusions
- [ ] complete artifact provenance and dependency compatibility review

### Repository
- [x] `CONTRIBUTING.md`
- [x] `GOVERNANCE.md`
- [x] `SECURITY.md`
- [x] `CONTRIBUTORS.md`
- [x] `docs/START-HERE-FOR-AGENTS.md`
- [x] `docs/licensing.md`

### Issues
- [x] requested labels created/verified
- [x] ten local task drafts and label taxonomy
- [x] twelve agent-ready issues published with frozen source SHAs; #1/#3/#5 are preferred pilot claims
- [x] shared research issue form covering reproduction, falsification and audit
- [ ] review pilot outcomes before publishing another task batch

### Automation
- [x] CI lint/tests; first hosted run passed on `0700f87`
- [x] existing protocol-isolation unit tests run in CI
- [ ] artifact consistency checks
- [x] PR template

### Outreach
- [ ] Moltbook project account
- [ ] thematic community
- [ ] first research challenge
- [x] contributor SKILL.md, format validated locally
- [ ] OpenClaw runtime loading and bounded execution verified

### Security
- [ ] recruiter sandbox
- [ ] no push token
- [ ] no secrets
- [ ] branch protection

Unchecked outreach and recruiter items are deferred, not requirements for the
first contribution. Existing read-only CI permissions do not establish recruiter
isolation or server-side branch protection.

# Part XIII. Phased rollout

## 35. Phase 0 — Legal and repository readiness

Goal: будь-який зовнішній contributor юридично і технічно розуміє правила.

Repository files and initial CI are complete. Before inviting untrusted execution,
verify branch protection, the private-report route and review ownership. Record
actual settings or blockers. Prepare an artifact-rights inventory before inviting
redistribution of datasets or trained artifacts. These checks do not delay static
source or literature review.

## 36. Phase 1 — Agent-ready tasks

Почати з трьох задач із [каталогу](agent-task-catalog.md):

1. OAC-01: перевірити, чи згортаються наявні блоки в одне перетворення.
2. OAC-03: перевірити походження та повноту запису останнього аудиту.
3. OAC-05: перевірити облік пам'яті готової моделі.

Для кожної зафіксувати повний source SHA, відповідального reviewer, дозволені
входи, очікуваний файл і критерій завершення. Не більше трьох активних задач
одночасно; одна основна задача на учасника. Інші чернетки залишаються в backlog.
Це початкові організаційні обмеження, які можна переглянути після пілота.

Після завершення або зупинки всіх трьох задач записати: що вдалося перевірити,
скільки часу витратив reviewer, які інструкції були незрозумілі та які результати
залишилися неперевіреними. Зупинений або негативний внесок також входить у звіт.
Не відкривати наступну партію, поки є внески без призначеного reviewer.

Далі підготувати одну незалежну репродукцію validation-only протоколу: точний
commit, версії залежностей, контроль потоків, команда, ліміт ресурсів, дозволені
дані та наперед визначені допуски для числових відмінностей. Час виконання
порівнювати з урахуванням обладнання. Це відтворення відомого результату, а не
нова перевірка на недоторканих даних. Не змінювати допуски після перегляду відповіді.

## 37. Phase 2 — Small Manual Outreach Pilot

Почати лише після проходження хоча б одного внеску через повний цикл
задача → PR → CI → review → запис рішення. Локальна репетиція перевіряє процес,
але не рахується незалежним внеском. Мати вільну задачу та reviewer перед запрошенням.

Обрати один доступний канал після перевірки його поточних правил і можливостей.
Moltbook залишається кандидатом, а створення акаунта чи спільноти не є критерієм
наукового прогресу. Спочатку один вручну перевірений research packet із посиланням
на конкретну задачу; публікація потребує окремого дозволу власника.

## 38. Phase 3 — Recruitment automation

Sandboxed recruiter регулярно знаходить релевантні дискусії і направляє contributors.

Автоматизація допускається після ручного пілота, який дав хоча б один перевірений
зовнішній внесок і показав прийнятне навантаження на review. Перед запуском
зафіксувати дозволені дії, бюджет, частоту повідомлень, спосіб вимкнення та
перевірку ізоляції. Якщо росте черга неперевірених внесків або надходять скарги
на повідомлення, призупинити recruitment і розібрати причину.

## 39. Phase 4 — Multi-platform federation

Recruitment не залежить від одного provider.

Не розгортати кілька каналів до оцінки першого. Окремо перевірити можливість
відновити репозиторій, задачі та evidence metadata з резервної копії без акаунта
власника. Git зберігає код, але не автоматично всі GitHub Issues, PR discussions
чи налаштування. Записати, що реально експортується і що потребує відновлення.

## 40. Phase 5 — Protocol-level contribution

Можливий майбутній machine-readable artifact:

`agent-tasks.json`

з task ID, type, priority, dependencies, data boundary та acceptance criteria.

Створювати цей формат тільки після виявленої потреби в пілоті. До того issue form
і каталог достатні; паралельні реєстри не повинні суперечити один одному.

# Part XIV. Success metrics

## 41. Primary

- independently reviewed reproductions, including failed reproductions;
- specific claims corrected or falsified with evidence;
- verified prior art that changes a research decision;
- completed audits, including explicit reports that no defect was found;
- research decisions supported by accepted evidence.

Count unique claims/results, not repeated PRs about the same result. Record the
denominator: attempted, completed, inconclusive and rejected tasks. Agent counts,
stars, posts, provider diversity and merged-PR counts are secondary context, not
evidence of scientific progress. Different model names do not establish independent
operators, environments or data boundaries.

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

Mitigation: GitHub as the current collaboration host, portable versioned evidence,
exported task/review metadata and a documented restore check. Multi-channel
discovery alone does not remove dependence on the host that stores the work.

## 53. Governance capture

Mitigation: transparent governance, recorded decisions, public protocols, reproducible releases.

# Part XVI. Immediate next actions

## 54. Priority 1 — Verify the Existing Contribution Path

Check repository settings and review ownership; record enforcement gaps. Keep
the owner-approved license choice and complete the separate provenance review.
Do not describe the completed repository foundation as a future deliverable.

## 55. Priority 2 — Publish Three Pilot Issues

Completed as an owner-requested expanded backlog of twelve live issues. Prefer
OAC-01, OAC-03 and OAC-05 for the first three claims; Erchard is the initial review
contact. Do not republish duplicates. Coordinate claims and review capacity now.

## 56. Priority 3 — Review the Pilot and Lock One Reproduction

Record all outcomes and review effort. Resolve ambiguous instructions, then lock
one validation-only reproduction with an explicit environment and numeric tolerances.

## 57. Priority 4 — Keep the Scientific Decision Moving

Use collapse and memory findings to choose one next DNS mechanism under the
[research plan](research-plan.md). Category theory remains a bounded supporting
analysis; neither outreach nor abstract formalization should block a justified
numerical experiment. No experiment starts without its own committed protocol.

## 58. Priority 5 — Manual Outreach and Portable Evidence

After the contribution path works, prepare one reviewed invitation to an available
task and a repository/task-metadata restore procedure. Select a platform based on
verified access and rules; no social account is a mandatory research dependency.

## 59. Priority 6 — Automate Only the Demonstrated Need

Deploy a recruiter or machine-readable task feed only after the pilot identifies
the need, review capacity and acceptable cost. Record a stop condition and keep
code execution, protected data and merge credentials outside outreach access.

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
