# Direct Computational Synthesis: від нейромережі до обчислювальної структури

> **Статус:** концептуальна дослідницька гіпотеза та майбутня програма робіт.  
> **Мова:** українська.  
> **Робоча назва:** Direct Computational Synthesis (DCS). Назва використовується як внутрішній ярлик і не є заявою про наукову новизну.  
> **Зв’язок із DNS:** DCS є ширшим можливим узагальненням Direct Network Synthesis, а не заміною поточної DNS-програми.

## 1. Коротка ідея

Поточна програма Direct Network Synthesis ставить питання:

> Чи можна корисні параметри або представлення нейромережі обчислити без довгого ітеративного підбору ваг?

Нова гіпотеза ставить ще ширше питання:

> Якщо нас цікавить не конкретна архітектура, а поведінка моделі, чи обов’язково кінцевою реалізацією цієї поведінки взагалі має бути нейромережа?

Умовно:

```text
Dataset / specification / teacher behavior
                  ↓
          learned computation
                  ↓
      structural extraction
                  ↓
     logical / algorithmic IR
                  ↓
     computational synthesis
                  ↓
optimized executable structure
```

Кінцева структура потенційно може бути гетерогенною:

- логічні вентилі;
- LUT;
- автомати станів;
- дерева рішень;
- таблиці;
- sparse linear transforms;
- dense matrix blocks;
- retrieval/memory blocks;
- невеликі neural subcircuits;
- спеціалізовані арифметичні блоки;
- або інша комбінація примітивів.

Найрадикальніша версія гіпотези:

> Нейромережа може бути не кінцевою формою інтелекту, а лише зручним механізмом пошуку складної функції. Після навчання цю функцію можна спробувати перекомпілювати в значно ефективнішу обчислювальну структуру.

## 2. Епістемічні позначки

- **[A]** — концептуальне міркування або аналогія;
- **[B]** — усталений математичний / цифрово-логічний факт;
- **[C]** — зв’язок з уже існуючими напрямами та інструментами;
- **[D]** — exploratory idea, яка ще не є канонічним результатом DNS;
- **[E]** — майбутня гіпотеза або експериментальна програма.

Жоден пункт [E] не слід подавати як доведений результат про великі мовні моделі.

# Part I. Вихідна аналогія: суматор як чорний ящик

## 3. Напівсуматор

Розглянемо чорний ящик з двома бітами входу `A`, `B` і двома бітами виходу `S`, `C`:

```text
A,B → [ ? ] → S,C
```

Його поведінка повністю задається таблицею істинності:

| A | B | S | C |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 0 | 1 | 1 | 0 |
| 1 | 0 | 1 | 0 |
| 1 | 1 | 0 | 1 |

З цієї таблиці видно:

```text
S = A XOR B
C = A AND B
```

Одна й та сама поведінка може мати дуже різні внутрішні реалізації:

```text
A,B → [велика нейромережа] → S,C
```

або:

```text
A,B → [XOR + AND] → S,C
```

Якщо обидві реалізації точні, їхній зовнішній функціональний контракт однаковий. Але фізична складність, енергія, затримка, площа та можливість формальної перевірки можуть відрізнятися на порядки. **[A][B]**

Центральна інтуїція:

> Велика модель може бути ефективним способом *знайти* функцію, але не обов’язково найефективнішим способом *виконувати* знайдену функцію.

## 4. Поведінка не визначає архітектуру

Якщо ми бачимо лише контракт:

```text
input → black box → output
```

то з самого контракту не випливає, що всередині повинна бути конкретна архітектура.

Для мовної моделі функціональний контракт можна записати як:

```text
context tokens → next-token logits / probabilities
```

Це опис поведінки, а не вимога використовувати Transformer. **[A]**

Сучасні LLM реалізуються нейромережами, зазвичай Transformer-подібними. Але це факт про поточні реалізації, а не математичний доказ, що кожна система з аналогічною поведінкою повинна мати таку саму внутрішню форму. **[B]**

# Part II. Що гарантовано можливо в принципі

## 5. Будь-яка фіксована цифрова модель є цифровою функцією

Якщо модель:

- працює з фіксованою цифровою точністю;
- має обмежену довжину входу;
- має визначене цифрове кодування входів і виходів;
- виконує скінченну кількість операцій для одного inference step;

то один її forward pass є скінченною цифровою функцією. **[B]**

У найзагальнішому вигляді:

```text
bit vector X → bit vector Y
```

Будь-яка така скінченна булева функція має реалізацію як булева схема. **[B]**

Отже, для фіксованої quantized neural network існує точне перетворення:

```text
quantized NN
    ↓
finite digital computation
    ↓
Boolean circuit
```

Це твердження саме по собі не дає ефективної схеми. Воно лише встановлює існування функціонально еквівалентної цифрової реалізації.

## 6. Універсальний логічний базис

NAND і NOR є функціонально повними базисами. **[B]**

Наприклад:

```text
NOT A = A NAND A
```

а AND, OR, XOR та довільні булеві функції можна побудувати композицією NAND.

Тому для будь-якої скінченної цифрової функції можна записати:

```text
model behavior
    ↓
Boolean circuit
    ↓
NAND-only circuit
```

Це універсальне проміжне представлення, але не обов’язково найкраща фізична реалізація.

## 7. Від універсального базису до реального заліза

Після логічної оптимізації можливий technology mapping:

```text
Boolean / NAND-level IR
        ↓
pattern recognition
        ↓
XOR / MUX / adder / comparator / LUT / standard cells
        ↓
physical implementation
```

Кінцева бібліотека залежить від носія:

- FPGA;
- ASIC;
- custom silicon;
- CPU;
- GPU accelerator;
- future hardware substrate.

# Part III. Дві принципово різні задачі

## 8. Наївна компіляція мережі

```text
NN operation
→ arithmetic circuit
→ gates
```

Кожне множення, додавання, порівняння тощо можна реалізувати цифровою логікою.

Такий шлях може дати:

```text
large NN
→ equally large or larger gate-level netlist
```

Це корисно для спеціалізованого hardware execution, але не вирішує головної ідеї DCS.

## 9. Семантична компіляція

Сильніша задача:

```text
large learned structure
        ↓
what function is actually being implemented?
        ↓
find equivalent simpler computation
```

Для суматора бажаний результат:

```text
1000-neuron network
        ↓
semantic extraction
        ↓
XOR + AND
```

а не буквальне розгортання 1000 нейронів у gates.

Саме це є головною невідомою DCS. **[E]**

## 10. Syntactic compilation vs semantic extraction

### Syntactic compilation

```text
matrix multiply → multiplier/adders → gates
```

### Semantic extraction

```text
large subnetwork → comparator
large subnetwork → parity circuit
attention pattern → finite-state transition
repeated computation → reusable macro
```

### Computational resynthesis

```text
extracted behavior
→ optimized heterogeneous implementation
```

# Part IV. Exact та approximate режими

## 11. Exact equivalence

Для малого дискретного простору:

```text
∀x: C(x) = N(x)
```

де `N` — teacher network, а `C` — synthesized circuit.

Приклади:

- XOR;
- half-adder;
- full-adder;
- multiplexer;
- comparator;
- parity;
- small ALU;
- bounded finite-state task.

Для таких задач можлива повна truth-table verification або formal equivalence checking. **[B]**

## 12. Approximate equivalence

Для великої моделі повна точна еквівалентність може бути надто дорогою або непотрібною.

Тоді можна оптимізувати:

```math
J(C) = Error(C,T)
     + λ1 Compute(C)
     + λ2 Memory(C)
     + λ3 Energy(C)
     + λ4 Area(C)
     + λ5 Latency(C)
```

де `T` — teacher behavior.

# Part V. LLM як чорний ящик

## 13. Функціональний контракт мовної моделі

Для одного autoregressive step:

```text
(context tokens, state)
        ↓
     [ model ]
        ↓
(next-token logits, new state)
```

Якщо vocabulary, context, arithmetic та state bounded, то один inference step є скінченною цифровою функцією. **[B]**

Теоретично він має circuit realization. Але з цього не випливає, що вона буде компактною.

## 14. Чому повний генератор — sequential system

LLM генерує послідовність токенів:

```text
state_t + token_t
        ↓
      circuit
        ↓
state_(t+1) + token_(t+1)
```

Тому реалістична hardware realization є sequential circuit / state machine with memory, а не лише combinational truth table.

Для Transformer state може включати context representation або KV cache.

Фраза «мікросхема повністю містить LLM» означає акуратно:

> статична функція моделі, її постійні параметри та inference machinery фізично реалізовані на чипі; динамічний контекст і runtime state все одно потребують пам’яті.

## 15. Ваги як дані проти структури як програми

Сьогодні:

```text
weights stored in memory
        ↓
compute engine reads weights
        ↓
matrix operations
```

DCS-альтернатива:

```text
trained weights / behavior
        ↓
compile
        ↓
physical computational topology
```

У крайній формі:

```text
weights-as-data
      ↓
computation-as-structure
```

Не всі numeric constants або memory обов’язково зникають. Частина може залишитися у ROM/SRAM/LUT.

# Part VI. Чип, який є моделлю

## 16. Поточний режим

```text
model file
   ↓
HBM / DRAM
   ↓
GPU / TPU
   ↓
load weights
   ↓
matmul
   ↓
store activations
   ↓
repeat
```

Ціна включає:

- зберігання ваг;
- рух ваг;
- рух активацій;
- synchronization;
- scheduling;
- універсальний control overhead.

## 17. DCS hardware target

```text
input tokens
    ↓
[ specialized model circuit ]
    ↓
next-token output
```

Усередині можуть бути:

- hardwired logic;
- local SRAM;
- ROM/LUT;
- sparse matrix engines;
- dense arithmetic islands;
- state machines;
- routing fabric;
- token/state buffers;
- small programmable regions.

## 18. Hard core + soft core + memory

```text
[ hard computational core ]
            +
[ reconfigurable / programmable region ]
            +
[ mutable memory / retrieval layer ]
```

- **hard core** — стабільна логіка та часто повторювані обчислення;
- **soft core** — adapters, змінні правила, task-specific extensions;
- **memory layer** — факти, персональні дані, retrieval, runtime state.

# Part VII. Потенційна енергетична вигода

## 19. Data movement

Типовий цикл:

```text
memory
→ weights
→ compute
→ activations
→ memory
→ next layer
```

Якщо частина computation hardwired:

```text
wire → gate → wire → gate
```

частина weight fetches та generic dispatch може зникнути. **[A][E]**

Потенційні джерела виграшу:

- constant propagation;
- common subexpression elimination;
- sparsity;
- dead-computation elimination;
- low precision;
- local wiring;
- custom arithmetic widths;
- domain-specific macros.

Енергетичний виграш треба вимірювати, а не припускати. **[E]**

## 20. Що може знищити вигоду

- netlist explosion;
- routing congestion;
- fan-out;
- велика площа;
- низька utilization;
- великі state buffers;
- clock/power distribution;
- надмірний synthesis time;
- погана updateability;
- duplication замість time-multiplexing.

DCS не припускає, що hardwiring автоматично кращий за GPU.

# Part VIII. Суміжні напрями

## 21. Logic synthesis

Berkeley ABC — зріла система synthesis/verification для binary sequential logic, з AIG, technology mapping та formal verification. **[C]**

- https://www-cad.eecs.berkeley.edu/~alanmi/abc/starting.htm
- https://github.com/berkeley-abc/abc

DCS потенційно може використовувати logic synthesis як backend.

## 22. FINN

FINN — open-source framework для quantized neural network inference на FPGA. **[C]**

- https://xilinx.github.io/finn/
- https://github.com/Xilinx/finn

Він показує, що neural network можна компілювати в customized dataflow architecture.

## 23. LogicNets

LogicNets перетворює quantized neurons із bounded fan-in у truth tables / LUT logic. **[C]**

- https://arxiv.org/abs/2004.03021
- https://github.com/Xilinx/logicnets

Ключова проблема: truth-table cost росте експоненційно з fan-in.

## 24. LUTNet

LUTNet використовує FPGA LUT як learned inference operators. **[C]**

- https://arxiv.org/abs/1910.12625

## 25. Чим DCS сильніше за звичайну NN-to-hardware compilation

Відомі підходи часто мають форму:

```text
quantized NN
→ FPGA/dataflow/LUT implementation
```

DCS ставить додаткове питання:

```text
trained model
→ identify actual learned computation
→ discard unnecessary neural representation
→ synthesize simpler heterogeneous structure
```

Жодної заяви про novelty робити не слід до систематичного related-work review.

# Part IX. Можлива архітектура DCS compiler

## 26. Stage 0 — Freeze the contract

Визначити:

- input encoding;
- output encoding;
- context bound;
- precision;
- deterministic/stochastic behavior;
- state semantics;
- allowed approximation.

## 27. Stage 1 — Quantize / discretize

Можливі режими:

- binary;
- ternary;
- int4;
- int8;
- fixed-point;
- mixed precision.

Розділяти:

```text
teacher error
vs
quantization error
vs
circuit synthesis error
```

## 28. Stage 2 — Build exact local functions

Для малих fragments:

```text
subnetwork inputs
→ subnetwork outputs
→ truth table
```

Потім:

- Boolean minimization;
- AIG optimization;
- BDD where feasible;
- SAT/SMT equivalence checking;
- LUT decomposition;
- don’t-care optimization.

## 29. Stage 3 — Discover reusable macros

- XOR/parity;
- comparator;
- adder;
- multiplexer;
- counter;
- finite-state transition;
- lookup;
- affine transform;
- threshold function;
- routing pattern.

## 30. Stage 4 — Global resynthesis

Layer boundaries teacher network не повинні бути недоторканними.

Це особливо цікаво в контексті DNS05, де кілька блоків, що проектують одну й ту саму fixed basis, можуть algebraically collapse в одну projection.

Питання DCS:

> яка частина apparent depth є реальною композиційною структурою, а яка — артефактом representation?

## 31. Stage 5 — Heterogeneous IR

```text
BOOL
LUT
FSM
AFFINE
SPARSE_MATMUL
DENSE_MATMUL
LOOKUP
MEMORY
ROUTER
REDUCE
NEURAL_BLOCK
```

Кожен block має typed inputs/outputs, bit width, state, latency, area/energy estimate та exact/approximate semantics.

## 32. Stage 6 — Technology mapping

Targets:

```text
CPU
FPGA
ASIC
```

Умовна cost function:

```math
Cost = α Area + β Delay + γ Energy + δ Memory + ε Updateability
```

# Part X. FPGA як перший hardware target

## 33. Чому FPGA

FPGA містить programmable LUT, routing, registers, DSP та memory blocks.

Переваги:

- фізична реалізація;
- перепрограмування;
- вимірювання latency/resources/power;
- не потрібен fabrication run;
- доступні open/academic synthesis tools.

Перший hardware milestone DCS логічніше робити на FPGA. **[E]**

# Part XI. ASIC як кінцева крайність

## 34. Коли ASIC має сенс

```text
trained teacher
      ↓
DCS extraction
      ↓
optimized netlist
      ↓
standard-cell mapping
      ↓
place & route
      ↓
ASIC
```

У крайній формі processor і model частково перестають бути окремими сутностями.

# Part XII. Основні гіпотези

## 35. H1 — Exact finite compilation

**[B]** Для bounded finite-precision inference function існує точна Boolean circuit realization.

## 36. H2 — Learned structural redundancy

**[E]** Для деяких задач:

```text
network size
≫
minimal equivalent computation size
```

## 37. H3 — Semantic macro extraction

**[E]** Можливо автоматично знаходити простіші symbolic/logical equivalents learned fragments.

## 38. H4 — Cross-layer simplification

**[E]** Частина trained depth може collapse при глобальному functional analysis.

## 39. H5 — Heterogeneous representation

**[E]** Оптимальна executable form може бути сумішшю computational primitives.

## 40. H6 — Lower inference cost after training

**[E]** Semantic resynthesis може зменшити state movement, arithmetic та memory traffic.

## 41. H7 — Training and deployment architectures need not match

**[E]**

```text
training architecture = search representation
execution architecture = compiled representation
```

# Part XIII. Найбільші перешкоди

## 42. Circuit minimization is hard

Факт існування компактної схеми не дає алгоритму її знаходження.

Реалістична мета:

> знайти значно кращу, а не гарантовано глобально мінімальну структуру.

## 43. Input-space explosion

Для `n` binary inputs truth table має `2^n` rows.

## 44. Precision explosion

Навіть int8 neuron з великим fan-in має величезний input domain.

## 45. State explosion

Context, KV cache, recurrence та memory можуть домінувати над logic.

## 46. Semantic irreducibility

Може виявитися, що велика частина моделі справді потребує складного розподіленого обчислення.

## 47. Hardware duplication vs time multiplexing

Fully unrolled hardware може різко збільшувати area.

## 48. Updateability

ASIC model швидко старіє.

# Part XIV. Перший експериментальний маршрут

## 49. Principle

Не починати з LLM.

Почати з задач, де:

- ground-truth function відома;
- minimal/near-minimal circuit відомий;
- повна еквівалентність перевіряється;
- hardware cost вимірюється.

## 50. DCS-0: Neural Half-Adder Recovery

Навчити навмисно надмірну neural network реалізовувати half-adder і автоматично відновити compact circuit.

Target:

```text
S = XOR(A,B)
C = AND(A,B)
```

Metrics:

- exact equivalence;
- gate count;
- logic depth;
- NAND-equivalent count;
- synthesis time;
- teacher parameter count;
- compression ratio;
- FPGA LUT count.

## 51. DCS-1: Full Adder

Порівняти:

1. known hand circuit;
2. naïve compiled NN circuit;
3. optimized extracted circuit.

## 52. DCS-2: Boolean benchmark suite

- XOR;
- parity;
- MUX;
- majority;
- comparator;
- encoder/decoder;
- small adder;
- small multiplier;
- popcount;
- small ALU.

## 53. DCS-3: Finite-state tasks

- parity stream;
- pattern detector;
- bounded counter;
- protocol parser;
- toy grammar;
- copy task;
- small regular languages.

Target:

```text
trained sequence model
→ finite-state machine / sequential circuit
```

## 54. DCS-4: Tiny bounded language model

Створити штучну мову з малим vocabulary, bounded context і відомою grammar/state structure.

Навчити tiny Transformer і спробувати відновити:

```text
grammar state
+ transition logic
+ lookup tables
```

## 55. DCS-5: Small real language model

Лише після успіху на synthetic language.

# Part XV. Baselines

## 56. Required baselines

1. original neural teacher;
2. naïve gate-level compilation;
3. standard logic synthesis of naïve circuit;
4. proposed semantic extraction;
5. hand-known reference circuit, якщо існує;
6. FPGA-oriented QNN/LUT baseline where applicable.

# Part XVI. Метрики

## 57. Functional correctness

Exact tasks:

```text
100% equivalence over complete input domain
```

Approximate tasks:

- output agreement;
- KL divergence;
- top-1 agreement;
- sequence-level behavior;
- downstream accuracy.

## 58. Structural metrics

- gate count;
- NAND-equivalent gate count;
- AIG node count;
- LUT count;
- logic depth;
- register count;
- memory bits;
- routing estimate;
- fan-in/fan-out distribution.

## 59. Physical metrics

На FPGA:

- LUTs;
- FFs;
- BRAM;
- DSP;
- max frequency;
- latency;
- throughput;
- power if possible.

Для ASIC estimate:

- standard-cell area;
- critical path;
- dynamic power;
- leakage;
- SRAM/ROM area;
- technology node assumptions.

## 60. Compilation metrics

- extraction time;
- peak RAM;
- solver calls;
- synthesis time;
- verification time;
- largest intermediate representation.

# Part XVII. Verification discipline

## 61. Exact equivalence before efficiency claims

На малих задачах optimized circuit повинна пройти exhaustive truth-table equivalence.

Потім, де можливо:

- SAT equivalence;
- SMT checks;
- formal sequential equivalence.

## 62. No hidden retraining

Розділяти:

```text
pure extraction
post-training optimization
retraining/distillation
```

## 63. Preserve negative results

Якщо:

```text
optimized circuit ≥ teacher cost
```

це важливий результат.

# Part XVIII. Відношення до DNS

## 64. DNS як підмножина більш широкої ідеї

DNS:

```text
Dataset
→ direct representation/weights
→ neural model
```

DCS:

```text
Dataset / teacher / specification
→ computational structure
```

У концептуальному сенсі:

```text
Direct Network Synthesis ⊂ Direct Computational Synthesis
```

Поточну емпіричну DNS-програму не слід переписувати через цю ідею.

DCS слід вести як окрему supporting/future branch, доки вона не отримає власні результати.

## 65. Два маршрути

### Route A — direct synthesis

```text
data
→ directly synthesize efficient computation
```

### Route B — train then compile

```text
data
→ conventional training
→ teacher NN
→ semantic extraction
→ efficient computation
```

Route B може бути практичнішим на ранньому етапі.

# Part XIX. Зв’язок з анти-монопольною метою

## 66. Потенційна користь

Якщо DCS зменшить inference cost, це може:

- дозволити локальний inference;
- зменшити залежність від великих GPU clusters;
- дозволити дешевші edge devices;
- зробити deployment незалежнішим від одного cloud provider;
- дозволити open FPGA/netlist implementations;
- збільшити кількість незалежних implementations.

## 67. Новий ризик монополії

Custom ASIC може посилити залежність від:

- semiconductor fabs;
- EDA vendors;
- advanced packaging;
- proprietary standard-cell libraries;
- capital-intensive fabrication.

Тому DCS не автоматично є anti-monopoly technology.

# Part XX. Non-claims

## 68. Що цей документ НЕ стверджує

- Не стверджується, що сучасний LLM можна сьогодні перетворити в маленьку NAND-схему.
- Не стверджується, що minimal circuit можна ефективно знайти для довільної функції.
- Не стверджується, що neural networks містять тисячократну semantic redundancy.
- Не стверджується, що ASIC завжди енергоефективніший за GPU.
- Не стверджується, що всі weights можуть бути усунуті.
- Не стверджується, що state/memory/context зникають.
- Не стверджується, що DCS є новим науковим напрямом.
- Не стверджується, що поточні DNS experiments є evidence for DCS.

# Part XXI. Критичне питання

## 69. Центральна невідома

> **Наскільки менша найкраща executable representation функції, яку вже знайшла велика нейромережа, порівняно із самою нейромережею?**

Для half-adder:

```text
large NN
≫
XOR + AND
```

Для реального LLM відповідь невідома.

Можливі результати:

### Weak result

```text
2× improvement
```

### Strong result

```text
10–100× improvement
```

### Transformative result

```text
orders-of-magnitude simplification
```

### Negative result

```text
minimal practical structure ≈ original learned structure
```

Усі чотири результати науково корисні.

# Part XXII. Найближчий практичний milestone

## 70. DCS proof-of-concept milestone

Для набору відомих Boolean functions:

1. train intentionally oversized neural teachers;
2. quantize/freeze them;
3. generate exact digital representations;
4. synthesize naïve circuits;
5. apply standard logic optimization;
6. apply proposed semantic extraction;
7. formally verify equivalence;
8. compare against hand-known circuits;
9. report gate count, depth, LUT usage, synthesis cost and compression ratio.

Ключовий тест:

> Чи може система автоматично пройти шлях від «навчена надмірна мережа» до «майже очевидна компактна логічна схема» без того, щоб ми вручну сказали їй, що це суматор або XOR?

# Part XXIII. Можливий майбутній stack

## 71. Conceptual toolchain

```text
Teacher model
    ↓
Model freezer
    ↓
Quantizer / finite semantics
    ↓
Graph decomposer
    ↓
Local function extractor
    ↓
Boolean / algebraic simplifier
    ↓
Macro recognizer
    ↓
Heterogeneous IR
    ↓
Formal verifier
    ↓
Cost optimizer
    ↓
┌──────────┬──────────┬──────────┐
│ CPU      │ FPGA     │ ASIC     │
│ backend  │ backend  │ backend  │
└──────────┴──────────┴──────────┘
```

## 72. Long-term vision

```text
TRAINING
neural network as search medium
          ↓

EXTRACTION
what computation was actually learned?
          ↓

SYNTHESIS
what is the cheapest representation of it?
          ↓

PHYSICAL REALIZATION
software / FPGA / ASIC / future substrate
```

Нейромережа може бути **чернеткою алгоритму**, а compiler — засобом перетворення цієї чернетки на кінцеву машину.

# Part XXIV. Перші задачі для зовнішніх агентів

## 73. Prior-art audit

Знайти й класифікувати:

- neural-to-Boolean compilation;
- BNN-to-gates;
- QNN-to-LUT;
- logic minimization of neural inference;
- symbolic extraction from trained networks;
- finite-state extraction from RNN/Transformer;
- program synthesis from neural behavior;
- FPGA neural compilation;
- ASIC hardwired inference;
- formal equivalence checking.

## 74. Microbenchmark implementation

Реалізувати DCS-0 / DCS-1:

- half-adder;
- full-adder;
- oversized MLP teacher;
- exact quantization;
- truth-table extraction;
- Boolean minimization;
- equivalence test;
- gate metrics.

## 75. Logic backend audit

Порівняти:

- Berkeley ABC;
- Yosys;
- FPGA synthesis flows;
- SAT-based equivalence tools.

# Part XXV. References / anchors

## 76. Logic and hardware synthesis

- Berkeley ABC: https://www-cad.eecs.berkeley.edu/~alanmi/abc/starting.htm
- Berkeley ABC GitHub: https://github.com/berkeley-abc/abc

## 77. Quantized neural networks to FPGA/dataflow logic

- FINN: https://xilinx.github.io/finn/
- LogicNets: https://arxiv.org/abs/2004.03021
- LogicNets code: https://github.com/Xilinx/logicnets
- LUTNet: https://arxiv.org/abs/1910.12625

Ці роботи показують, що neural inference вже може бути co-designed із LUT/FPGA logic. Вони не доводять сильнішу DCS-гіпотезу про масштабну semantic resynthesis загальної trained model у радикально простішу non-neural machine.

# Conclusion

Direct Computational Synthesis пропонує ширший погляд, ніж Direct Network Synthesis.

Замість припущення:

```text
AI = neural network
```

ми розглядаємо:

```text
behavior
→ computation
→ representation
→ physical implementation
```

Research target:

> **Find the simplest practical executable structure that preserves the required behavior, regardless of whether that structure still looks like the neural network that originally discovered it.**

Half-adder — мінімальний motivating example:

```text
large learned black box
→ exact functional analysis
→ XOR + AND
```

Long-term question:

> Чи існує meaningful analogue такого спрощення для learned language and reasoning systems?

У цьому проєкті це питання поки що відкрите.
