# Error-Driven Computational Synthesis (EDCS)
## Навчання обчислювальної структури з нуля через структурне виправлення помилок

> **Статус:** концептуальна дослідницька гіпотеза та програма майбутніх експериментів.  
> **Мова:** українська.  
> **Робоча назва:** Error-Driven Computational Synthesis (EDCS). Назва є внутрішнім ярликом і не є заявою про наукову новизну.  
> **Зв’язок із проєктом:** EDCS природно продовжує Direct Network Synthesis (DNS) і Direct Computational Synthesis (DCS), але ставить окреме, сильніше питання.  
> **Ключовий принцип:** не навчати параметри всередині заздалегідь заданої архітектури, а ітеративно будувати та редагувати саму обчислювальну структуру у відповідь на помилки.

---

# 1. Звідки виникає ця ідея

Попередня лінія міркувань була такою.

Спочатку розглядалася нейромережа як чорний ящик:

```text
input
  ↓
[ neural network ]
  ↓
output
```

Потім було поставлено питання: якщо поведінка системи вже відома, чи обов’язково кінцева реалізація повинна залишатися нейромережею?

Це привело до DCS:

```text
trained neural network
        ↓
semantic extraction
        ↓
equivalent computation
        ↓
optimized circuit / program / heterogeneous machine
```

Наступний крок: якщо така скомпільована машина помиляється на нових прикладах, можливо, не потрібно перебудовувати її повністю. Якщо існує універсальний алгоритм, який знаходить невелику структурну зміну, що усуває помилку, тоді можна уявити:

```text
current circuit C
       ↓
observed error
       ↓
structural diagnosis
       ↓
small patch ΔC
       ↓
improved circuit C'
```

Звідси виникає головний крок.

Якщо алгоритм структурного виправлення справді є загальним і не потребує того, щоб початкова схема вже була «розумною», тоді **навчена нейромережа більше не потрібна навіть як стартова точка**.

Можна почати з тривіальної машини:

```text
inputs
  ↓
[ almost empty computation ]
  ↓
default outputs
```

і трактувати її як систему, яка просто помиляється майже на всіх нетривіальних прикладах.

Тоді кожна помилка стає приводом для структурної зміни.

Отже:

```text
C0 = trivial computation

example 1 → error → ΔC1 → C1
example 2 → error → ΔC2 → C2
example 3 → error → ΔC3 → C3
...
```

Модель не має фіксованої архітектури, яку людина придумала до навчання.

**Архітектура сама стає результатом навчання.**

---

# 2. Центральна гіпотеза EDCS

Головне питання:

> **Чи можна навчати довільну обчислювальну структуру безпосередньо, починаючи з тривіальної схеми, за допомогою універсального error-driven structural update algorithm, який із прикладів помилкової поведінки знаходить корисні локальні зміни структури?**

У найбільш короткій формі:

```text
examples
   ↓
errors
   ↓
structural credit assignment
   ↓
structural edits
   ↓
emergent computation
```

Формально:

```math
C_0 = C_{\text{trivial}}
```

На кроці `t`:

```math
\hat y_t = C_t(x_t)
```

після отримання правильного результату `y_t`:

```math
e_t = Compare(\hat y_t, y_t)
```

далі:

```math
\Delta C_t = Repair(C_t, x_t, y_t, H_t)
```

де `H_t` — історія, protected examples, constraints та інша інформація, потрібна для збереження вже правильної поведінки.

Після цього:

```math
C_{t+1} = Simplify(C_t \oplus \Delta C_t)
```

де `⊕` означає структурне редагування.

На відміну від gradient descent, об’єктом навчання є не лише вектор параметрів:

```math
\theta \in \mathbb{R}^n
```

а сама обчислювальна машина:

```math
C \in \mathcal{C}
```

де `𝒞` — простір допустимих програм, схем, автоматів, пам’яті та їх композицій.

---

# 3. Чим це принципово відрізняється від звичайної нейромережі

## 3.1 Звичайне навчання

У стандартній нейромережі людина заздалегідь визначає:

- тип шарів;
- їх кількість;
- ширину;
- правила з’єднання;
- механізм attention;
- activation functions;
- тип стану;
- спосіб проходження даних.

Після цього навчаються числові параметри:

```text
fixed architecture
      +
learned weights
```

Умовно:

```math
\theta_{t+1} = \theta_t - \eta \nabla_\theta L
```

## 3.2 EDCS

У EDCS можна зафіксувати лише мінімальну «фізику» системи:

- допустимі примітиви;
- допустимі структурні операції;
- правила стану та пам’яті;
- цільову функцію;
- алгоритм пошуку/ремонту.

А сама структура виникає під час навчання:

```text
primitive computational substrate
            ↓
        examples
            ↓
     structural edits
            ↓
emergent architecture
```

Отже:

```text
architecture ≠ fixed design
architecture = learned artifact
```

---

# 4. «Порожня схема» не означає відсутність припущень

Це критично важливе уточнення.

EDCS не створює систему «без індуктивного упередження».

Навіть якщо `C0` майже порожня, ми все одно задаємо:

1. **мову примітивів**;
2. **множину допустимих структурних змін**;
3. **функцію вартості**;
4. **стратегію пошуку**;
5. **правила збереження старої поведінки**;
6. **тип пам’яті та стану**;
7. **критерій того, що вважається кращим рішенням**.

Саме ці речі стають аналогом архітектурного inductive bias.

Тому правильніше казати не:

> «ми прибрали архітектуру»,

а:

> **ми перестали фіксувати кінцеву архітектуру до навчання і перенесли inductive bias на рівень правил структурного росту та вартості.**

---

# 5. Що таке `C0`

Найпростіша початкова система повинна мати визначений інтерфейс:

```text
Inputs → C0 → Outputs
```

Для combinational task:

```text
C0(x) = constant output
```

наприклад усі нулі.

Для sequential task потрібно також визначити початковий state:

```text
(state0, input) → output, state1
```

Тобто навіть «порожня» система має:

- input ports;
- output ports;
- можливо state ports;
- default behavior.

Наприклад:

```text
A ─┐
   ├── [ C0 ] ── S = 0
B ─┘            C = 0
```

для half-adder.

Це вже коректна машина.

Вона просто недостатньо добре описує бажану функцію.

---

# 6. Навчання як послідовність структурних ремонтів

Нехай маємо dataset:

```math
D = \{(x_i,y_i)\}_{i=1}^N
```

На кожному кроці:

1. подаємо `x_i`;
2. отримуємо `ŷ_i = C_t(x_i)`;
3. порівнюємо з `y_i`;
4. якщо результат неправильний — викликаємо `Repair`;
5. отримуємо candidate patch;
6. перевіряємо його;
7. застосовуємо лише якщо він покращує визначену objective.

Схематично:

```text
          ┌────────────────────────────┐
          │                            │
          │       current C_t          │
          │                            │
          └─────────────┬──────────────┘
                        │
                      input
                        │
                        ↓
                    prediction
                        │
                  compare with y
                        │
              ┌─────────┴─────────┐
              │                   │
           correct              error
              │                   │
              │                   ↓
              │           structural diagnosis
              │                   ↓
              │              candidate ΔC
              │                   ↓
              │              verification
              │                   ↓
              └──────────→ C_(t+1)
```

---

# 7. Універсальний Repair-оператор

Центральний недоведений об’єкт EDCS:

```math
Repair(C, E, P, B) \rightarrow \Delta C
```

де:

- `C` — поточна структура;
- `E` — failing examples / error evidence;
- `P` — protected behavior, яке не можна зламати;
- `B` — resource budget / constraints;
- `ΔC` — структурна зміна.

Repair не повинен бути ручним правилом для кожної задачі.

Його амбіція:

> **один загальний алгоритм структурного credit assignment та resynthesis для широкого класу задач.**

---

# 8. Можливі стадії Repair

## 8.1 Error localization

Спочатку визначити, які output bits / symbols / states неправильні.

```text
actual:   101001
desired:  101101
              ^
        wrong region
```

## 8.2 Dependency tracing

Для circuit representation можна пройти назад по графу залежностей.

```text
wrong output
     ↑
 node 91
  ↑     ↑
n37    n54
 ↑       ↑
...
```

Таким чином отримуємо **causal cone** — підграф, який може впливати на помилку.

Елементи поза ним не потрібно розглядати для локального ремонту цього виходу.

## 8.3 Editable cut selection

Потрібно вибрати boundary:

```text
upstream fixed logic
       ↓
[ editable region R ]
       ↓
downstream fixed logic
```

Repair може:

- редагувати існуючі gates;
- замінити весь region;
- вставити bypass;
- створити додаткову гілку;
- додати state;
- змінити LUT;
- змінити routing.

## 8.4 Constraint construction

Для failing examples:

```math
C'(x_i)=y_i
```

Для protected examples:

```math
C'(z_j)=C(z_j)
```

або:

```math
Quality(C',P) \ge Quality(C,P)-\epsilon
```

## 8.5 Candidate synthesis

Знайти `R'`, який задовольняє constraints і має мінімальну або малу вартість.

Можливі механізми:

- SAT;
- SMT;
- exact logic synthesis;
- enumerative search;
- local graph rewriting;
- stochastic search;
- learned repair policy;
- hybrid symbolic + learned search.

EDCS не визначає наперед, який solver виявиться масштабованим.

## 8.6 Verification

Перевірити:

- failing examples виправлені;
- protected behavior не зламане;
- structural constraints виконані;
- cost не перевищено.

## 8.7 Commit

Тільки після перевірки:

```text
C_t + verified patch
        ↓
C_(t+1)
```

---

# 9. Мова структурних змін

Мінімальний набір edit operations може виглядати так:

```text
ADD_NODE(type)
REMOVE_NODE(id)
REPLACE_NODE(id, type)
ADD_EDGE(src, dst)
REMOVE_EDGE(src, dst)
REWIRE_EDGE(...)
CHANGE_LUT(...)
ADD_CONSTANT(...)
ADD_STATE(...)
REMOVE_STATE(...)
REPLACE_SUBGRAPH(...)
INSERT_BYPASS(...)
INSERT_SELECTOR(...)
```

Якщо базис NAND-only:

```text
ADD_NAND
REMOVE_NAND
REWIRE
```

теоретично достатньо для combinational Boolean logic.

Для реальної sequential AI system потрібні також state/memory primitives.

Наприклад:

```text
NAND
REGISTER
RAM_READ
RAM_WRITE
MUX
CLOCK / EVENT
```

або більш високорівнева heterogeneous IR.

---

# 10. Structural credit assignment

У neural backpropagation ключова проблема:

> які параметри відповідальні за помилку?

Gradient дає числовий sensitivity signal.

В EDCS аналогічна проблема:

> **яка частина структури відповідальна за помилку і яка структурна зміна має найкраще співвідношення correction / collateral damage / complexity?**

Робочий термін:

**Structural Credit Assignment**

або:

**Structural Backpropagation**

але другий термін не означає, що використовується математичний backpropagation.

Порівняння:

```text
Neural:
error
  ↓
gradient attribution
  ↓
Δweights

EDCS:
error
  ↓
causal / structural attribution
  ↓
Δgraph
```

---

# 11. Чому «виправляти кожну помилку окремо» недостатньо

Є тривіальний алгоритм, який формально може навчитися training set.

Для кожного прикладу додавати:

```text
if input == x1: output y1
if input == x2: output y2
...
```

Це lookup table.

Вона може мати нульову training error і нульове корисне узагальнення.

Тому EDCS — не просто patching.

Головна вимога:

> **Repair повинен шукати структурну зміну, яка пояснює множину випадків компактніше, ніж їх незалежне запам’ятовування.**

---

# 12. Складність як джерело узагальнення

Можлива objective:

```math
J(C) =
L(C,D)
+ \lambda_1 Complexity(C)
+ \lambda_2 UpdateCost(C,C_{old})
+ \lambda_3 RuntimeCost(C)
+ \lambda_4 MemoryCost(C)
```

де:

- `L` — помилка;
- `Complexity` — структурна складність;
- `UpdateCost` — величина зміни;
- `RuntimeCost` — latency / operations;
- `MemoryCost` — state / storage.

У локальному ремонті:

```math
\Delta C^*
=
\arg\min_{\Delta C}
[
L(C\oplus\Delta C,D)
+\lambda Complexity(\Delta C)
+\mu Damage(C,\Delta C,P)
]
```

Ідея близька до принципу:

> якщо дві гіпотези однаково пояснюють відомі дані, перевагу має компактніша.

Це MDL/Occam-подібна інтуїція, але EDCS не стверджує, що одна лише мінімальна схема гарантує generalization.

---

# 13. Half-adder як мінімальний приклад

Training table:

| A | B | S | C |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 0 |
| 1 | 0 | 1 | 0 |
| 1 | 1 | 0 | 1 |

Початок:

```text
S = 0
C = 0
```

### Example 1

```text
00 → 00
```

Помилки немає.

### Example 2

```text
01 → 10
```

Repair має знайти зміну.

### Example 3

```text
10 → 10
```

Якщо попередня зміна була тупим memorization patch, потрібен ще один patch.

Якщо cost function винагороджує спільне пояснення, може з’явитися структура, яка охоплює обидва випадки.

### Example 4

```text
11 → 01
```

Після повного набору бажаний compact result:

```text
S = A XOR B
C = A AND B
```

Критичний тест:

> Чи може EDCS знайти логічно еквівалентну компактну схему без того, щоб алгоритму було сказано, що задача є half-adder?

---

# 14. Архітектура як learned object

У традиційному ML:

```text
human chooses architecture
machine learns parameters
```

У EDCS:

```text
human chooses substrate + update law
machine learns computation
```

Можлива еволюція:

```text
NAND
 ↓
repeated local motifs
 ↓
XOR-like structures
 ↓
adders / selectors / comparators
 ↓
state machines
 ↓
algorithmic modules
 ↓
higher abstractions
```

Ці рівні не обов’язково повинні бути названі або задані наперед.

Якщо macro discovery корисний, система може сама вводити reusable blocks.

---

# 15. Автоматичне утворення нових примітивів

Припустимо, підсхема `G` зустрічається тисячі разів.

Система може:

1. довести/оцінити її функцію;
2. створити macro primitive `M`;
3. замінити повторення на `M`;
4. додати `M` у бібліотеку доступних конструкцій.

Тоді «мова мислення» системи може еволюціонувати:

```text
base primitives
      ↓
learned motifs
      ↓
learned macros
      ↓
larger reusable computational concepts
```

Це потенційно різко змінює search complexity.

Водночас macro creation може створити lock-in у невдалу абстракцію, тому потрібна можливість:

- inline;
- split;
- rewrite;
- deprecate;
- resynthesize.

---

# 16. Навчання не тільки topology, а й representation

EDCS не зобов’язаний навчати лише gate graph.

Навчуваним може бути:

```text
topology
+ constants
+ bit widths
+ state variables
+ memory layout
+ routing
+ macros
+ control flow
+ representation format
```

Тобто кінцева система може бути heterogeneous machine:

```text
logic
+ memory
+ lookup
+ arithmetic
+ state machines
+ neural islands
+ symbolic blocks
```

Головне — не тип компонента, а те, що його поява повинна бути виправдана поведінкою та cost function.

---

# 17. Чи потрібні взагалі нейрони

У EDCS нейрон — лише один можливий primitive.

Система може мати primitive:

```text
NEURAL_BLOCK
```

якщо це виявляється компактним способом реалізації певної поведінки.

Тоді EDCS не є «анти-нейронною» концепцією.

Вона каже:

> **не слід апріорі вимагати, щоб уся система була нейромережею.**

Якщо neural block оптимальний — він залишається.

Якщо XOR, FSM або LUT дешевші — використовуються вони.

---

# 18. Continual learning природно випливає з EDCS

Після початкового навчання система продовжує отримувати нові приклади.

```text
C_t
 ↓
new experience
 ↓
detected mismatch
 ↓
Repair
 ↓
C_(t+1)
```

Отже, initial training і later fine-tuning більше не є фундаментально різними процесами.

Це одна й та сама операція:

```math
C_{t+1}=Repair(C_t,\text{new evidence})
```

Різниця лише в тому, наскільки зріла поточна структура.

---

# 19. Хірургічне виправлення і preservation

Для зрілої системи дуже важливо не ламати правильну поведінку.

Тому `Repair` має оптимізувати не лише:

```text
fix new error
```

а:

```text
fix new error
+
preserve validated behavior
```

Можливе формулювання:

```math
\min_{\Delta C} Cost(\Delta C)
```

за умов:

```math
(C\oplus\Delta C)(x_i)=y_i
```

для failing examples і:

```math
(C\oplus\Delta C)(z_j)=C(z_j)
```

для protected examples.

Це структурний аналог conservative fine-tuning.

---

# 20. Новий факт і новий алгоритм — різні типи змін

Для зрілої AI system потрібно розрізняти:

### Factual update

```text
"X is currently Y"
```

Можливо, правильна зміна — лише запис у mutable memory.

### Behavioral correction

```text
system systematically misinterprets negation
```

Може вимагати logic patch.

### New skill

```text
system learns a new transformation
```

Може вимагати нового module.

### Representation failure

```text
current architecture cannot express required behavior efficiently
```

Може вимагати глобальної перебудови.

Тому хороший Repair повинен спочатку класифікувати тип зміни.

---

# 21. Не все має бути hardwired

Навіть якщо кінцева система реалізована в hardware, EDCS не вимагає, щоб усе було immutable logic.

Практична архітектура може мати:

```text
┌─────────────────────────────┐
│ Stable compiled core        │
├─────────────────────────────┤
│ Reconfigurable logic        │
├─────────────────────────────┤
│ Mutable knowledge memory    │
├─────────────────────────────┤
│ Runtime state               │
├─────────────────────────────┤
│ Patch / update controller   │
└─────────────────────────────┘
```

Таке розділення дозволяє дешеві factual updates і структурні upgrades без повної заміни пристрою.

---

# 22. Локальні patches не можуть накопичуватися безкінечно

Після великої кількості локальних ремонтів:

```text
Core
+ Patch 1
+ Patch 2
+ ...
+ Patch 100000
```

структура може стати:

- надлишковою;
- повільною;
- суперечливою;
- складною для verification;
- погано оптимізованою глобально.

Тому EDCS потребує другого процесу.

---

# 23. Consolidation / global resynthesis

Періодично:

```text
current core
+ accumulated patches
+ protected behavior
+ accumulated data
        ↓
global resynthesis
        ↓
cleaner C_new
```

Цілі consolidation:

- прибрати redundant patches;
- об’єднати повторювані правила;
- відкрити macros;
- перепакувати state;
- зменшити circuit size;
- зменшити latency;
- скоротити memory traffic;
- позбутися історичних артефактів.

Отже, життєвий цикл:

```text
local learning
    ↓
patch accumulation
    ↓
consolidation
    ↓
new stable core
    ↓
local learning
    ↓
...
```

---

# 24. Навчання як versioned evolution

Кожна структурна зміна може бути explicit diff.

Наприклад:

```text
Update 4812

Reason:
  failing examples F381..F402

Modified:
  nodes 81291..81307

Added:
  12 gates
  1 state bit

Removed:
  7 gates

Verified:
  402 failing cases fixed
  1,200,000 protected cases unchanged
```

Це створює можливість:

- audit;
- rollback;
- bisect;
- compare;
- merge;
- attribution;
- safety review.

Тобто з’являється щось на кшталт:

> **Git for computational intelligence.**

---

# 25. Merge двох незалежно навчених систем

Якщо дві копії походять від одного base:

```text
C0
├── branch A → C_A
└── branch B → C_B
```

можна визначити:

```text
ΔA = diff(C0, C_A)
ΔB = diff(C0, C_B)
```

і спробувати:

```text
Merge(C0, ΔA, ΔB)
```

Конфлікт можна визначати не лише syntactically, а behaviorally:

- patches змінюють один region;
- patches змінюють overlapping input domains;
- один patch руйнує guarantees іншого;
- structural resources collide.

Це відкриває окремий напрям **distributed learning by mergeable structural patches**.

---

# 26. EDCS як альтернативний погляд на backpropagation

Backpropagation відповідає:

> як із output error отримати numerical credit assignment для ваг?

EDCS намагається відповісти:

> як із output error отримати structural credit assignment для самої машини?

Порівняння:

```text
BACKPROP

fixed topology
     ↓
forward
     ↓
error
     ↓
gradient
     ↓
small numerical changes


EDCS

mutable topology
     ↓
execute
     ↓
error
     ↓
structural diagnosis
     ↓
graph/program changes
```

EDCS не обов’язково є gradient-free у кожному внутрішньому solver. Наприклад, learned repair policy може використовувати neural optimization.

Ключове — **об’єкт глобального навчання є структура, а не фіксований tensor parameterization**.

---

# 27. Де знаходиться «ітеративність»

Початковий DNS досліджував можливість уникнути iterative parameter optimization.

EDCS, навпаки, прямо допускає ітеративність:

```text
C0 → C1 → C2 → ... → Cn
```

Але ітерації мають іншу природу.

DNS:

```text
можливо обчислити representation напряму?
```

EDCS:

```text
можливо вчити computation як послідовність structural repairs?
```

Це не суперечність.

Це два різні дослідницькі маршрути.

---

# 28. Відношення DNS → DCS → EDCS

## DNS

```text
Dataset
   ↓
direct synthesis
   ↓
Neural representation / weights
```

Питання:

> чи можна отримати корисну neural model без довгого gradient search?

## DCS

```text
Dataset / teacher / specification
   ↓
computational synthesis
   ↓
efficient executable structure
```

Питання:

> чи повинна кінцева модель взагалі залишатися нейромережею?

## EDCS

```text
trivial computation
   ↓
examples + errors
   ↓
structural repair iterations
   ↓
emergent executable structure
```

Питання:

> чи можна взагалі будувати computation з нуля через універсальний error-driven structural learning algorithm?

Умовно:

```text
DNS:  learn weights differently
DCS:  compile learned function differently
EDCS: learn the computation itself
```

---

# 29. Найсильніша версія EDCS

Якщо гіпотеза працює дуже добре:

1. не потрібна заздалегідь спроєктована Transformer architecture;
2. не потрібен величезний dense weight space;
3. не потрібна окрема post-training compilation фаза;
4. architecture, memory і algorithms виникають під час learning;
5. deployment representation уже є продуктом learning;
6. continual learning використовує той самий Repair;
7. фізична структура може оновлюватися локально.

У цій версії:

```text
DATA
  ↓
EDCS
  ↓
COMPUTATION
```

без проміжного обов’язкового:

```text
NEURAL NETWORK
```

---

# 30. Але EDCS не є «навчанням без архітектури»

Це одна з найважливіших non-claims.

Замість Transformer architecture ми задаємо **meta-architecture**:

```text
primitive language
+ edit language
+ repair algorithm
+ complexity metric
+ verifier
+ memory semantics
+ consolidation policy
```

Тому головне питання зміщується:

> Який structural learning law породжує ефективні обчислення?

Це аналог питання:

> Яке правило локального оновлення породжує корисну глобальну організацію?

---

# 31. Related work: CEGIS

Counterexample-Guided Inductive Synthesis (CEGIS) — важливий conceptual relative.

CEGIS ітеративно:

1. синтезує candidate program;
2. перевіряє його;
3. отримує counterexample;
4. додає counterexample до constraints;
5. синтезує нового candidate.

Умовно:

```text
candidate
   ↓
verify
   ↓
counterexample
   ↓
synthesize
   ↓
new candidate
```

Це показує, що error/counterexample-driven iterative construction program already exists as a general synthesis paradigm.

Ключова відмінність можливої EDCS-програми:

> не лише перевипускати candidate program, а масштабовано локалізувати відповідальність і виконувати **мінімальний структурний repair** великої вже існуючої системи, з preservation constraints і continual learning.

Related anchors:

- Armando Solar-Lezama, *Program Synthesis by Sketching*.
- *Program sketching*, STTT.
- CEGIS(T) literature.

References:

- https://link.springer.com/article/10.1007/s10009-012-0249-7
- https://digicoll.lib.berkeley.edu/record/134841/
- https://link.springer.com/chapter/10.1007/978-3-319-96145-3_15

---

# 32. Related work: program synthesis

Program synthesis загалом будує programs із specification.

Типове формулювання:

```math
\exists P \; \forall x : \sigma(P,x)
```

Тобто потрібно знайти program `P`, який задовольняє specification.

EDCS є близьким за духом, але фокусується на:

- learning from behavioral evidence;
- incremental structural change;
- preservation of previous behavior;
- open-ended growth;
- cost-aware local repair;
- potential hardware realization;
- continual learning.

Reference overview:

- https://pmc.ncbi.nlm.nih.gov/articles/PMC5597726/

---

# 33. Related work: logic synthesis and rewriting

Класичний logic synthesis already performs:

- Boolean simplification;
- AIG rewriting;
- refactoring;
- technology mapping;
- equivalence checking.

Berkeley ABC, наприклад, містить DAG-aware AIG rewriting і equivalence verification.

Це важливо, тому що EDCS не повинен винаходити ці backend techniques повторно.

Вони можуть бути нижнім шаром:

```text
EDCS repair proposal
       ↓
logic synthesis
       ↓
optimized equivalent region
```

References:

- https://github.com/berkeley-abc/abc
- https://people.eecs.berkeley.edu/~alanmi/

---

# 34. Related work: SAT-based exact synthesis

SAT-based exact synthesis намагається знайти circuit, який задовольняє задану truth table / specification, часто з мінімальними structural metrics.

Це особливо релевантно для малих EDCS repair regions.

Reference:

- Winston Haaswijk et al., *SAT-Based Exact Synthesis: Encodings, Topology Families, and Parallelism*.
- https://people.eecs.berkeley.edu/~alanmi/publications/2020/tcad20_exact.pdf

Це сильний candidate backend для proof-of-concept, але exact synthesis runtime погано масштабується.

---

# 35. Related work: genetic programming

Genetic programming також шукає executable structures, а не лише numerical weights.

Типовий GP:

```text
population of programs
      ↓
evaluate fitness
      ↓
selection / mutation / crossover
      ↓
new population
```

Схожість з EDCS:

- структура є search object;
- architecture не фіксується як neural tensor graph.

Відмінність EDCS-гипотези:

- error localization;
- causal repair;
- minimal local structural delta;
- strong preservation constraints;
- versionable patches;
- continuous incremental improvement.

EDCS хоче уникнути сліпого глобального structural search, якщо локальний defect можна виправити хірургічно.

---

# 36. Related work: structural plasticity

У computational neuroscience та adaptive rewiring існує ідея, що learning може змінювати не тільки strength connections, а й topology:

- adding connections;
- pruning connections;
- network rewiring.

Це концептуально близько до EDCS, але EDCS фокусується не на біологічній правдоподібності, а на synthesis of arbitrary executable computation.

One review anchor:

- *Adaptive rewiring: a general principle for neural network development*
- https://pmc.ncbi.nlm.nih.gov/articles/PMC11554485/

---

# 37. Де може бути власне нове питання

Без prior-art audit не можна заявляти novelty.

Але сильна комбінація, яку слід перевіряти, виглядає так:

```text
1. start from trivial executable structure
2. observe behavioral errors
3. localize structural responsibility
4. synthesize minimum-cost structural patch
5. preserve old behavior explicitly
6. repeat indefinitely
7. periodically consolidate
8. allow architecture and abstractions to emerge
9. compile/run directly on hardware-oriented substrate
```

Потрібен systematic literature review, щоб визначити, які частини вже досліджені разом або окремо.

---

# 38. Найбільша проблема: search space

Якщо дозволити довільні circuits, кількість можливих structures колосальна.

Навіть для малих Boolean functions exact circuit minimization є складним combinatorial problem.

Тому універсальний Repair може виявитися немасштабованим.

Це головний ризик.

---

# 39. Найбільша проблема: locality may be false

Невелика behavioral correction не гарантує невелику structural correction.

Може виявитися:

```text
small change in desired function
        ↓
large change in optimal circuit
```

Особливо якщо стара структура globally compressed.

Тоді surgical learning може часто вимагати large-scale resynthesis.

Це falsifiable question.

---

# 40. Найбільша проблема: preserving behavior

Protected dataset ніколи не є повним для великого input space.

Patch може:

```text
fix observed failure
```

але створити:

```text
unknown regressions elsewhere
```

Тому потрібно:

- formal verification where possible;
- invariants;
- property tests;
- held-out data;
- adversarial counterexample search;
- regression suites;
- confidence boundaries.

---

# 41. Найбільша проблема: generalization

Compactness не гарантує правильного generalization.

Можуть існувати багато однаково компактних circuits, які збігаються на training data і розходяться elsewhere.

Отже, EDCS все одно потребує inductive bias.

Питання:

> який bias у structural search дає корисне generalization на реальних задачах?

---

# 42. Найбільша проблема: continuous domains

Pure Boolean EDCS природний для finite digital functions.

Але real-world ML часто працює з:

- continuous signals;
- noise;
- uncertainty;
- probabilities.

Один варіант — fixed-point discretization.

Інший — heterogeneous primitives, де arithmetic blocks залишаються arithmetic.

EDCS не повинен штучно перетворювати все в NAND, якщо це робить representation гіршою.

---

# 43. Найбільша проблема: sequence state

LLM — не combinational function одного короткого input.

Потрібні:

- memory;
- state;
- recurrence;
- context;
- potentially huge dynamic storage.

Тому EDCS для language systems повинен навчати не лише Boolean logic, а **stateful computation**.

---

# 44. Найбільша проблема: credit assignment depth

Для великої системи causal cone одного output може охоплювати майже всю машину.

Тоді просте graph tracing не дає достатньої localization.

Потрібні більш сильні notions:

- causal influence;
- counterfactual dependency;
- minimal cut;
- information flow;
- symbolic sensitivity;
- learned responsibility model.

---

# 45. Найбільша проблема: update order

Ітеративний algorithm може залежати від порядку прикладів:

```text
D order A → circuit C_A
D order B → circuit C_B
```

Навіть якщо обидва мають однакову training accuracy.

Потрібно дослідити:

- order sensitivity;
- curriculum;
- replay;
- batch repair;
- consolidation.

---

# 46. Найбільша проблема: local minima of structure

Локально дешевий patch може зробити майбутню структуру гіршою.

Наприклад:

```text
cheap patch now
→ creates awkward dependency
→ many expensive patches later
```

Тому Repair може потребувати lookahead або periodic global restructuring.

---

# 47. Найбільша проблема: cost function

Якщо cost сильно карає complexity:

```text
underfit
```

Якщо слабко:

```text
memorize everything
```

Отже, `Complexity`, `Error`, `UpdateCost`, `Latency`, `Memory` та інші terms формують саме те, що система вважатиме хорошим знанням.

Cost function є частиною learning law.

---

# 48. EDCS-0: перший proof of concept

## Мета

Перевірити не «чи можна синтезувати half-adder».

Це давно відомо.

Перевірити:

> **чи може generic error-driven repair loop, почавши з тривіальної схеми, дійти до compact equivalent circuit без task-specific knowledge?**

## Allowed knowledge

Algorithm знає:

- число input/output bits;
- primitive library;
- edit operations;
- complexity metric;
- verification procedure.

Algorithm **не знає**:

- що це adder;
- що потрібен XOR;
- hand-designed structure.

---

# 49. EDCS-0 protocol

### Step 1

```text
C0:
S = 0
C = 0
```

### Step 2

Подати examples у preregistered order.

### Step 3

Для кожної помилки:

```text
localize
→ synthesize patch
→ verify all seen examples
→ minimize
→ commit
```

### Step 4

Після кожного commit записати:

- circuit;
- patch diff;
- gate count;
- depth;
- training truth-table coverage;
- synthesis time.

### Step 5

Наприкінці exhaustive verification по всій truth table.

### Success

- exact function;
- compact circuit;
- result substantially smaller than memorization baseline;
- algorithm did not receive task-specific templates.

---

# 50. EDCS-1: Function discovery benchmark

Tasks:

- AND;
- OR;
- XOR;
- XNOR;
- majority;
- parity;
- MUX;
- decoder;
- comparator.

Мета:

> перевірити, чи Repair bias систематично знаходить reusable logical structure.

---

# 51. EDCS-2: Arithmetic structures

Tasks:

- half-adder;
- full-adder;
- 2-bit adder;
- 4-bit adder;
- popcount;
- small multiplier.

Ключове питання:

> чи виникає modular reuse?

Наприклад, чи 4-bit adder будується через повторюваний carry structure, а не як giant truth-table patchwork.

---

# 52. EDCS-3: Hidden compositionality

Дати функцію, де правильна структура має hierarchy:

```text
subfunction A
subfunction B
      ↓
composition
```

Перевірити, чи EDCS відкриває modules.

---

# 53. EDCS-4: Sequential learning

Tasks:

- pattern detector;
- running parity;
- counter;
- finite regular language;
- tiny protocol.

Початковий machine state мінімальний.

Repair має право:

- add state bit;
- add transition;
- add logic.

Target:

```text
examples over time
→ emergent FSM
```

---

# 54. EDCS-5: Toy language

Створити synthetic language з відомою grammar/state machine.

Наприклад:

- vocabulary 16–64 tokens;
- bounded context;
- deterministic grammar;
- hidden states known only evaluator.

EDCS отримує sequences і desired next token.

Питання:

> чи може structural learning відкрити grammar machine без Transformer architecture?

---

# 55. EDCS-6: Probabilistic toy language

Додати stochastic outputs.

Тоді synthesized system повинна представляти distributions.

Це вимагає primitives для:

- probability;
- counting;
- normalization;
- stochastic selection або logits.

Це міст до language modeling.

---

# 56. Baselines

Кожен EDCS experiment повинен мати:

1. lookup-table memorization;
2. direct exact synthesis from full specification;
3. standard logic minimization;
4. genetic/evolutionary search baseline where feasible;
5. small neural network;
6. decision tree / symbolic baseline where applicable;
7. EDCS repair loop.

Мета — не просто показати, що EDCS «може розв’язати» задачу, а зрозуміти:

> що дає incremental structural repair порівняно з уже відомими способами synthesis.

---

# 57. Основні метрики

## Correctness

- train error;
- validation error;
- exhaustive truth-table accuracy where finite;
- sequence correctness.

## Structure

- gates;
- nodes;
- edges;
- circuit depth;
- state bits;
- memory bits;
- macro count;
- reused subgraphs.

## Learning

- number of repair steps;
- average patch size;
- max patch size;
- fraction of steps needing global resynthesis;
- time per repair;
- peak memory.

## Stability

- regressions introduced;
- protected behavior retained;
- rollback frequency.

## Generalization

- unseen input accuracy;
- held-out function regions;
- systematic compositional tests.

## Hardware

- LUT count;
- FF count;
- BRAM;
- latency;
- frequency;
- energy where measured.

---

# 58. Ключова нова метрика: Structural Update Ratio

Визначимо:

```math
SUR_t = \frac{Size(\Delta C_t)}{Size(C_t)}
```

Якщо mature system зазвичай має:

```math
SUR \ll 1
```

це підтримує ідею surgical learning.

Якщо кожне суттєве нове знання вимагає:

```math
SUR \approx 1
```

локальна структурна адаптація не працює.

---

# 59. Ключова нова метрика: Repair Generalization

Patch не повинен лише виправляти triggering example.

Нехай `F` — triggering failures, а `N(F)` — related unseen cases.

Можна вимірювати:

```math
RG =
\frac{\text{new related cases fixed}}
{\text{patch complexity}}
```

Це спроба виміряти, чи patch виявляє rule, а не memorizes case.

---

# 60. Ключова нова метрика: Consolidation Gain

До consolidation:

```text
C_before
```

Після:

```text
C_after
```

при еквівалентній/прийнятно близькій поведінці.

```math
CG =
1 - \frac{Cost(C_{after})}{Cost(C_{before})}
```

Це показує, чи локальні patches можна перетворювати назад у compact global structure.

---

# 61. Falsification criteria

EDCS слід вважати слабким або негативним напрямом, якщо:

1. Repair майже завжди деградує до lookup memorization.
2. Patch size швидко стає порівнянним із total model size.
3. Regression rate стає некерованим.
4. Global resynthesis потрібна майже після кожного update.
5. Search cost росте швидше, ніж benefit.
6. Learned structures значно гірші за стандартні synthesis algorithms.
7. Generalization не кращий за trivial baselines.
8. Architecture growth вибухає.
9. Sequential/stateful tasks не масштабуються.
10. Hardware cost не має переваги.

Негативний результат важливий, бо він покаже, чому fixed differentiable architectures є настільки успішними.

---

# 62. Що означатиме сильний результат

Сильний evidence:

```text
trivial C0
→ generic repairs
→ compact circuits
```

на багатьох функціях, причому:

- без task templates;
- з малою кількістю structural edits;
- із good unseen generalization;
- з reusable modules;
- з predictable scaling.

Ще сильніше:

```text
combinational
→ sequential
→ grammar-like
```

без зміни core learning law.

---

# 63. Що означатиме трансформативний результат

Найсильніша версія:

> один і той самий structural update law здатний із experience вирощувати складні, модульні, stateful computational systems, які конкурентні neural models за quality, але компактніші та дешевші в execution.

Тоді:

```text
fixed architecture + learned weights
```

перестає бути єдиною практичною парадигмою machine learning.

---

# 64. Потенційний hardware loop

Якщо target substrate reconfigurable:

```text
physical C_t
   ↓
observe error
   ↓
compute patch
   ↓
partial reconfiguration
   ↓
physical C_(t+1)
```

Тобто learning може буквально змінювати hardware topology.

Для immutable ASIC можна мати:

- spare regions;
- programmable routing;
- FPGA-like islands;
- patch LUTs;
- external correction layer.

---

# 65. Самомодифікована AI system

У далекій версії:

```text
AI executes
   ↓
AI observes failures
   ↓
AI runs Repair on itself
   ↓
formal/self tests
   ↓
AI deploys verified patch
```

Це вже self-modifying computational system.

Така система потребує дуже жорсткого safety boundary:

- protected core;
- signed patches;
- verification;
- rollback;
- immutable recovery image;
- permission boundaries.

Це окрема safety/program-verification проблема, а не автоматичний наслідок EDCS.

---

# 66. Розподілене навчання

Можлива модель:

```text
Base C0
├── Agent A learns → ΔA
├── Agent B learns → ΔB
├── Agent C learns → ΔC
```

Після independent validation:

```text
Merge(ΔA, ΔB, ΔC)
        ↓
C1
```

Тоді knowledge contribution може бути не giant checkpoint, а маленький structural patch.

Потенційно:

```text
"ось виправлення здатності X"
```

стає portable artifact.

Це добре узгоджується з метою low provider lock-in.

---

# 67. Економічна мотивація

Якщо EDCS працює:

- training може використовувати менше dense compute;
- model state може бути компактнішим;
- inference може використовувати specialized logic;
- local updates можуть бути дешевшими;
- improvements можуть поширюватися як patches;
- незалежні групи можуть merge contributions;
- не обов’язково розповсюджувати multi-hundred-GB weight checkpoints.

Це лише потенційний наслідок.

Його потрібно вимірювати.

---

# 68. Ризик нової залежності

Якщо EDCS сильно прив’язаний до:

- proprietary synthesis engine;
- proprietary FPGA;
- closed EDA;
- one vendor’s IR;
- one hardware fabric;

він може створити новий lock-in.

Тому для broader project goals бажані:

- open structural IR;
- open patch format;
- reproducible Repair;
- multiple backends;
- open verification;
- portable behavioral tests.

---

# 69. Proposed EDCS artifact stack

```text
edcs/
├── ir/
│   ├── circuit
│   ├── state
│   └── patch
├── repair/
│   ├── localize
│   ├── synthesize
│   ├── verify
│   └── score
├── simplify/
├── consolidate/
├── backends/
│   ├── software
│   ├── yosys
│   └── abc
├── benchmarks/
│   ├── boolean
│   ├── arithmetic
│   ├── sequential
│   └── toy_language
└── metrics/
```

Це лише possible future layout, не план негайної перебудови repository.

---

# 70. Мінімальний Patch IR

Наприклад:

```json
{
  "base_hash": "...",
  "reason": "fails examples 17,18",
  "operations": [
    {"op": "add_gate", "id": "g41", "type": "NAND"},
    {"op": "connect", "from": "x1", "to": "g41.a"},
    {"op": "connect", "from": "x2", "to": "g41.b"},
    {"op": "rewire", "from": "g41.out", "to": "y0"}
  ],
  "verified_examples": 128,
  "cost_delta": 4
}
```

Така форма робить learning auditable.

---

# 71. Repair pseudocode

```text
function REPAIR(C, failures F, protected P, budget B):

    affected_outputs = locate_output_errors(F)

    cone = backward_dependency_cone(
        C,
        affected_outputs
    )

    candidate_regions = choose_editable_regions(
        cone,
        budget=B
    )

    best = NONE

    for region in candidate_regions:

        constraints = build_constraints(
            failures=F,
            protected=P,
            boundary=region.boundary
        )

        replacement = synthesize_region(
            constraints,
            primitives=C.primitives,
            budget=B
        )

        if replacement does not exist:
            continue

        C_candidate = replace(
            C,
            region,
            replacement
        )

        C_candidate = simplify(C_candidate)

        if not verify(C_candidate, F, P):
            continue

        score = objective(C_candidate, C)

        if best is NONE or score < best.score:
            best = C_candidate

    return best
```

Це не готовий scalable algorithm.

Це executable research specification того, що треба винайти.

---

# 72. Batch repair

Для generalization краще часто давати Repair не один приклад:

```text
(x,y)
```

а cluster:

```text
F = {
  related failures,
  near misses,
  contrasting correct cases
}
```

Так algorithm може знаходити decision boundary / rule, а не memorization patch.

---

# 73. Active counterexample discovery

Після patch можна навмисно шукати input, де стара та нова системи розходяться:

```text
find x such that:
C_old(x) != C_new(x)
```

Потім evaluator визначає:

- зміна бажана;
- regression;
- невизначено.

Це зближує EDCS із counterexample-guided synthesis.

---

# 74. Learning loop із verifier

Більш сильний цикл:

```text
evidence
   ↓
Repair
   ↓
candidate C'
   ↓
Verifier / adversary
   ↓
counterexample?
   ├── yes → Repair again
   └── no  → commit
```

Це може бути ключем до надійного structural learning на formalizable domains.

---

# 75. Training data як specification fragments

У EDCS кожен training example можна бачити не лише як point in loss landscape, а як constraint:

```math
C(x_i)=y_i
```

Навчання поступово накопичує constraints.

Але generalization потребує compression цих constraints у reusable structure.

У цьому сенсі:

```text
learning = constraint accumulation + structural compression
```

---

# 76. Можливий фундаментальний погляд

Можна сформулювати learning так:

> **Навчання — це побудова дедалі компактнішої executable theory, яка пояснює дедалі більшу множину спостережень.**

Тоді:

- data = observations;
- errors = contradictions;
- Repair = theory revision;
- circuit = executable theory;
- consolidation = simplification;
- generalization = predictions theory outside observed examples.

Це філософське формулювання, а не доказ.

Але воно добре описує EDCS research intuition.

---

# 77. Чому ця ідея може провалитися фундаментально

Можливо, neural networks працюють добре саме тому, що:

- continuous parameter space гладкий;
- gradient дає дешевий local direction;
- distributed representations дозволяють smooth generalization;
- discrete structural search занадто discontinuous;
- local edits мають непередбачувані global effects.

Тоді EDCS може бути корисний лише для малих symbolic domains.

Це важлива competing hypothesis.

---

# 78. Hybrid route

Навіть якщо pure EDCS не масштабується, можлива гібридна система:

```text
structural EDCS outer loop
        ↓
neural / differentiable inner blocks
```

Наприклад Repair може вирішити:

```text
цей region краще замінити маленьким neural block
```

а його weights навчити gradient descent.

Після цього block можна знову спробувати скомпілювати.

Тоді:

```text
structure learning
+
parameter learning
```

не є взаємовиключними.

---

# 79. EDCS як meta-learning architecture

Ще один варіант:

Repair сам може бути learned model.

```text
Repair_φ(C, failures) → patch
```

І `φ` навчається на тисячах малих synthesis tasks.

Тоді система може «навчитися ремонтувати».

Це не зменшує цінність EDCS formulation.

Навпаки, воно відокремлює:

```text
object being learned = computation C
learning mechanism = Repair_φ
```

---

# 80. Найчистіший перший науковий тест

Перший експеримент має бути максимально простим.

Не LLM.

Не FPGA.

Не energy claims.

А:

> **Чи може універсальний local structural repair algorithm, отримуючи лише input/output constraints, виростити compact Boolean circuits із trivial initial circuit і робити це краще за memorization?**

Якщо відповідь «ні» на half-adder, parity, MUX і small arithmetic — немає сенсу говорити про масштабування.

Якщо «так» — наступне питання:

> чи зберігається перевага зі зростанням compositional depth та state?

---

# 81. Recommended first implementation

Для першого prototype:

### Representation

AIG або simple NAND DAG.

### State

None.

### Solver

SAT/exact synthesis на bounded local region.

### Repair strategy

1. start constant output;
2. on failure, enlarge editable cone radius;
3. synthesize smallest replacement satisfying all seen examples;
4. standard logic minimize;
5. verify;
6. commit.

### Tasks

- XOR;
- majority;
- MUX;
- half-adder.

### Compare

- full truth-table exact synthesis;
- local incremental EDCS;
- lookup memorization.

Це дозволить відокремити саму incremental idea від усіх майбутніх складнощів.

---

# 82. Перший сильний негативний тест

Взяти functions, де локальні corrections конфліктують.

Наприклад:

- parity;
- hidden global dependency;
- functions з avalanche-like behavior.

Перевірити:

> чи змушують вони EDCS перебудовувати майже всю схему?

Це критичний тест locality hypothesis.

---

# 83. Naming

Робочі назви:

### Error-Driven Computational Synthesis — EDCS

Підкреслює:

```text
error → synthesis update
```

### Incremental Computational Synthesis — ICS

Підкреслює:

```text
C_t → C_(t+1)
```

### Structural Learning

Загальніша, але занадто широка назва.

### Structural Error Correction

Добре описує Repair, але не повний learning process.

### Adaptive Circuit Learning

Добре для hardware-focused branch.

Поки **EDCS** найбільш точно описує центральний loop.

---

# 84. Non-claims

Цей документ **не стверджує**, що:

- універсальний scalable Repair algorithm уже існує;
- circuit learning масштабуватиметься до LLM;
- локальна behavioral error завжди має локальне structural fix;
- minimal circuits автоматично generalize;
- NAND-only representation буде практичною для AI;
- gradient descent більше не потрібен;
- structural learning дешевший за neural training;
- hardware self-modification є безпечним;
- EDCS є науково новою концепцією;
- current DNS/DCS experiments є evidence for EDCS;
- architecture-free learning possible без inductive bias.

---

# 85. Центральна невідома

Всю програму можна стиснути до одного питання:

> **Чи існує практично масштабований закон структурного оновлення, який із помилок поточної машини здатний поступово будувати дедалі кращу, компактну та узагальнюючу обчислювальну структуру?**

У формулі:

```math
C_{t+1}=Repair(C_t,E_t)
```

із бажаними властивостями:

```math
Error(C_{t+1}) < Error(C_t)
```

```math
Size(\Delta C_t) \ll Size(C_t)
```

для локальних оновлень,

```math
Generalization(C_{t+1}) \ge Generalization(C_t)
```

у середньому,

та прийнятним:

```math
ComputeCost(Repair)
```

---

# 86. Якщо відповідь позитивна

Тоді традиційна схема:

```text
human designs architecture
        ↓
random parameters
        ↓
gradient training
        ↓
trained neural network
```

отримує альтернативу:

```text
human defines computational substrate
        ↓
trivial machine
        ↓
examples / errors
        ↓
structural repair
        ↓
emergent machine
```

І кінцевий результат одразу є executable computational structure.

---

# 87. Найбільш радикальний висновок

Початкова проблема DNS звучала приблизно:

> чи можна створювати neural models без дорогого iterative weight search?

DCS розширив її:

> чи повинна learned function взагалі залишатися neural network?

EDCS робить ще один крок:

> **можливо, нам не потрібно починати з нейромережі взагалі. Можливо, потрібно навчати саму обчислювальну структуру.**

Тоді нейронна мережа стає лише одним із можливих історичних способів реалізації learning.

Не фундаментом.

---

# 88. Long-term vision

```text
               EXPERIENCE
                   ↓
              discrepancy
                   ↓
        STRUCTURAL CREDIT ASSIGNMENT
                   ↓
                REPAIR
                   ↓
        executable structure C_t
                   ↓
             verification
                   ↓
           continued operation
                   ↓
                new data
                   ↓
                  ...
```

Періодично:

```text
patch history
+ learned modules
+ accumulated constraints
        ↓
consolidation
        ↓
simpler, cleaner C_new
```

У далекій перспективі:

```text
experience
→ self-modifying computation
→ portable structural patches
→ reconfigurable hardware
```

---

# 89. Коротка теза для README / майбутнього abstract

> **Error-Driven Computational Synthesis explores whether a useful computational system can be learned from a trivial initial machine by iteratively repairing its executable structure in response to behavioral errors. Unlike conventional neural training, the target of learning is not a fixed architecture’s parameters but the architecture, state, memory, and computation themselves. The central open question is whether a general structural repair rule can produce compact, generalizing, and locally updatable machines at useful scale.**

Українською:

> **Error-Driven Computational Synthesis досліджує, чи можна навчити корисну обчислювальну систему, починаючи з тривіальної машини та ітеративно виправляючи її виконувану структуру у відповідь на помилки поведінки. На відміну від звичайного neural training, об’єктом навчання є не параметри фіксованої архітектури, а сама архітектура, стан, пам’ять і спосіб обчислення. Центральне відкрите питання — чи може загальне правило структурного ремонту породжувати компактні, узагальнюючі та локально оновлювані машини в практичному масштабі.**

---

# 90. Related-work anchors for the first audit

Ці джерела є стартовими точками, а не доказом novelty або її відсутності:

1. Armando Solar-Lezama, *Program Synthesis by Sketching*  
   https://digicoll.lib.berkeley.edu/record/134841/

2. Armando Solar-Lezama, *Program sketching*  
   https://link.springer.com/article/10.1007/s10009-012-0249-7

3. *Program synthesis: challenges and opportunities*  
   https://pmc.ncbi.nlm.nih.gov/articles/PMC5597726/

4. CEGIS(T) / Counterexample-Guided Inductive Synthesis Modulo Theories  
   https://link.springer.com/chapter/10.1007/978-3-319-96145-3_15

5. Berkeley ABC — logic synthesis and formal verification  
   https://github.com/berkeley-abc/abc

6. Winston Haaswijk et al., *SAT-Based Exact Synthesis: Encodings, Topology Families, and Parallelism*  
   https://people.eecs.berkeley.edu/~alanmi/publications/2020/tcad20_exact.pdf

7. *Adaptive rewiring: a general principle for neural network development*  
   https://pmc.ncbi.nlm.nih.gov/articles/PMC11554485/

Перший prior-art task повинен шукати також:

- incremental circuit synthesis;
- ECO (engineering change order) logic optimization;
- logic patch synthesis;
- automated program repair;
- incremental program synthesis;
- neuroevolution / topology evolution;
- Cartesian genetic programming;
- circuit learning;
- structure learning;
- self-modifying programs;
- continual program synthesis;
- lifelong synthesis;
- grammar induction;
- FSM inference;
- symbolic regression;
- minimum description length program learning.

---

# 91. Підсумок

EDCS виникає з дуже простої логіки.

Якщо ми вміємо:

```text
current machine
+ known error
→ useful structural correction
```

і цей механізм універсальний, тоді не існує принципової причини вимагати, щоб current machine на першому кроці вже була навченою neural network.

Можна почати з:

```text
C0 = trivial machine
```

і трактувати навчання як:

```text
wrong behavior
→ structural correction
→ better machine
→ new error
→ new correction
→ ...
```

Отже:

```text
learning
≠ necessarily weight optimization
```

Можливе альтернативне визначення:

> **Learning is the iterative construction and revision of executable computation under behavioral evidence and complexity constraints.**

Саме цю гіпотезу EDCS пропонує перевіряти.
