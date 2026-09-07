# План експериментів DCS та EDCS

Дата: 2026-09-07. Статус: запланована програма, не виконані експерименти.
Це не виконуваний preregistration: runner, backend і машинні конфігурації ще
потрібно реалізувати, перевірити та закомітити до оцінювання.
[Methodology](methodology.md) залишається обов'язковою.

## 1. Мета та вихідний стан

DCS перевіряє, чи можна виконувати знайдену функцію дешевшою структурою.
EDCS перевіряє, чи можна навчати саму структуру через виправлення помилок.
Це різні питання; EDCS є ітеративним пошуком, а не навчанням за один прохід.

Перевірено код DNS04, DNS05 і перелік runners/configs/tests: наявні SVD/ReLU,
kernel compiler, ridge та streaming diagnostics. DCS extractor, circuit IR,
структурний Repair і відповідні експериментальні runners відсутні.
Наявні результати DNS не є свідченнями на користь DCS або EDCS.

Порядок: закрити звіт DNS05-BM, виконати CS-A0, потім DCS-V0/DCS-C1,
після окремого рішення EDCS-V0/EDCS-L1. EDCS-U2 та CS-S3 умовні.
Одночасно активний лише один новий експериментальний механізм.
Негативний DCS-C1 не спростовує EDCS, але не дає підстав масштабувати DCS.
Завершити звіт означає перевірити вже наявний артефакт, а не повторити test run.

## 2. CS-A0: аудит і підготовка

1. Порівняти neural-to-logic compilation, CEGIS, exact synthesis, incremental
   synthesis та automated program repair. Для кожного джерела записати, які
   припущення, алгоритми та обмеження реально прочитані.
2. Обрати відтворюваний open-source backend для логічної оптимізації та
   bounded SAT synthesis; зафіксувати версію, ліцензію, solver seed і команду.
   Не писати власний SAT solver. Відсутність робочого backend є blocker.
3. Спільне початкове представлення: ациклічний AIG, двовходові AND,
   інверсії на ребрах, константи, іменовані входи/виходи; без стану й RAM.
   Рахувати AND nodes, ребра, інверсії, глибину та serialized bytes окремо.
4. Підготувати незалежний інтерпретатор для перевірки схеми, серіалізацію,
   replay patch, контроль циклів і незмінності захищених прикладів.
5. Зафіксувати encoding, overflow/rounding, output threshold/ties,
   порядок candidates та deterministic tie-breaking до оцінювання.

Бюджет підготовки: до 8 годин роботи. Результат: коротка таблиця prior art,
перевірений backend і список невирішених питань. Якщо backend не працює,
зафіксувати blocker, а не підміняти його ручними рішеннями для benchmark.

Початкові джерела, перевірені 2026-09-07:

- [ABC README](https://github.com/berkeley-abc/abc): доступні AIG rewriting
  та перевірка еквівалентності; це кандидат backend, а не наша новизна.
- [LogicNets, abstract](https://arxiv.org/abs/2004.03021): перетворення
  quantized neurons на truth tables потребує контролю fan-in. Повний
  аналіз реалізації та чесного baseline залишається завданням CS-A0.
- [Program sketching, abstract](https://link.springer.com/article/10.1007/s10009-012-0249-7):
  CEGIS поєднує синтез із прикладів і перевірку з новими counterexamples.
- [SAT-Based Exact Synthesis, abstract](https://si2.epfl.ch/demichel/publications/archive/2020/winston-exact.pdf):
  exact synthesis має непередбачуваний runtime; потрібні жорсткі ліміти.

Це початкова перевірка джерел, не завершений аудит новизни. Недоступні під
час пошуку Berkeley PDF та thesis URL не вважаються прочитаними повністю.

## 3. Два режими доказів

**Verification fixtures (V0).** Вся мала специфікація відкрита. Повний
перебір перевіряє програмну коректність, але не є ML benchmark або test accuracy.
Результат: `equivalence_pass`, кількість перевірених входів, контрприклади.
Це unit/integration checks, не виняток із data-separation protocol для моделей.

**Експерименти C1/L1/U2.** Окремі train/validation/test; навчання, включно
з protected constraints, використовує лише train. Validation обирає тільки
наперед визначені налаштування. Test відкривається один раз для фінального
порівняння. Жодні test counterexamples не повертаються Repair.
Ранні development runs залишають test fields null.

Рівність двох схем на всьому домені може перевірятися без task labels:
це формальна перевірка трансформації, а не сигнал для навчання.
Якщо алгоритм отримує teacher-відповіді на додаткових входах, вони входять
до synthesis-data manifest. Такий режим не можна видавати за equal-data
навчання лише на початковому train; у першому C1 додаткові запити заборонені.

## 4. DCS-V0: точна трансформація

Задачі: XOR, half-adder, full-adder, majority-3, MUX із двома data inputs.
Використати задані скінченні integer-threshold мережі та їх надлишкові копії.
Це сконструйовані fixtures, не результат навчання. Не підбирати мережу,
доки вона випадково стане зручною для extraction.

Порівняння: буквальне переведення мережі в логіку; те саме зі стандартною
оптимізацією ABC; локальна функціональна заміна; відома ручна схема як reference.
Один backend і одна цільова бібліотека для всіх структурних порівнянь.
Кандидат extraction: повна таблиця локального фрагмента з не більш ніж
4 boundary bits, generic resynthesis і перевірена заміна. Без назв задач,
ручних XOR/adder templates та доступу extractor до коду цільової функції.

Gate: усі еквівалентності точні, навмисно пошкоджені схеми відхиляються,
round-trip і replay відтворюють виходи. Будь-яка хибна еквівалентність блокує C1.
Саме зменшення надмірної fixture не є науковим доказом semantic advantage.

## 5. DCS-C1: користь понад стандартну оптимізацію

Гіпотеза: локальна функціональна заміна зменшує вартість уже стандартно
оптимізованого neural computation, зберігаючи точний цифровий контракт.

1. Використати задачі та п'ять розбиттів із секції 8. Навчити один невеликий
   teacher на train, вибрати його лише на validation і заморозити.
2. Перед запуском зафіксувати архітектуру, навчальний алгоритм, число кроків,
   quantization і всю сітку вибору. Навчання teacher може бути градієнтним;
   його ціну й помилки рахувати окремо. Не називати цей маршрут direct training.
3. Порівняти frozen teacher; literal compilation; literal + ABC; local
   resynthesis + той самий ABC. Компактний hand reference показувати окремо:
   він знає задачу, тому не є equal-data learner.
4. Обмежити local boundary до 4 bits і один детермінований sweep. Перевіряти
   еквівалентність заміни для всіх локальних assignments, без task labels.
   Непідтримуваний fan-in або quantization failure записувати, не обходити.
5. Виміряти окремо помилки teacher, quantization і compilation, число nodes,
   глибину, bytes, extraction/verification time, peak RAM та inference time.

Основне порівняння: local resynthesis + ABC мінус literal + ABC.
Попередній practical gate: точна еквівалентність у всіх завершених runs;
медіанне скорочення nodes не менше 20% на щонайменше двох структурованих
задачах, без збільшення глибини понад 10%, у межах бюджету. Це критерій
продовження, не обіцянка результату чи доведений hardware speedup.
Якщо ABC вже прибирає всю надлишковість, результат негативний саме для
доданої extraction. Не замінювати baseline слабшим після оцінювання.

## 6. EDCS-V0 та EDCS-L1: вирощування структури

V0: ті самі малі відкриті fixtures; початкова схема повертає нулі.
Перевірити generic repair, збереження всіх побачених прикладів, replay і rollback.
У C0 вихід не залежить від входів: Repair повинен мати право додати primary
inputs та нові зв'язки. Пошук лише в наявному dependency cone не може стартувати.

L1: перевірити користь локального ремонту з неповних даних.

1. Подавати train у зафіксованому порядку; checkpoints після 16/32/64/128
   прикладів. На checkpoint використовувати всі побачені constraints,
   незалежно від того, які приклади попередня схема класифікувала правильно.
2. Основний candidate: bounded local repair, до 8 нових AND nodes на patch,
   до 4 boundary bits; якщо локального рішення немає, дозволено один global
   fallback із загальним лімітом 256 nodes. Частоту fallback звітувати явно.
3. Comparator: пересинтез із C0 на кожному тому самому checkpoint, ті самі
   constraints, primitive library, solver та загальний часовий бюджет.
   Обидва методи мінімізують nodes, потім depth, потім canonical serialization.
4. Додати lookup із train-only majority default, decision tree, linear ridge,
   RBF ridge і deterministic ReLU + ridge. Mandatory DNS baselines не прибирати.
   Зафіксувати їх сітки й однакові validation allowances перед запуском.
5. Лише одна додаткова ablation: local repair без global fallback. Якщо не
   знайдено patch, залишити попередню схему та записати невиправлені constraints;
   не приховувати цей run і не видавати timeout за неможливість розв'язку.

Основні порівняння: час повної траєкторії local+fallback проти rebuild;
paired accuracy і nodes фінальних моделей. Зберігати learning curves,
train regressions, patch size, solver failures та global rebuild fraction.

Попередній gate на development: не менше 25% медіанного зниження total learning
time проти rebuild на двох структурованих задачах; paired mean accuracy не
гірша більш ніж на 1 percentage point; nodes не більші більш ніж на 10%.
Мають завершитися всі п'ять paired runs цих задач. Перевага лише над lookup
не достатня. Всі інші задачі, включно з негативними, залишаються у звіті.
Граничні та суперечливі outcomes означають inconclusive, не перемогу.

## 7. EDCS-U2 та CS-S3: умовне продовження

U2 перевіряє, чи компактна машина дійсно дешево оновлюється.
Після L1 і до нового test access зафіксувати окремий update protocol:
порівняти repair і повний rebuild для двох типів змін бажаної функції:
обмежена зміна на заданій області та глобальна зміна, наприклад інверсія parity.
Старі constraints у зміненій області потрібно замінити, а не вимагати одночасно
стару й нову відповідь. Retention оцінюється на незміненій області.
Окремо виміряти consolidation on/off, повну ціну перевірок і new/old accuracy.
Пари мають однакові старі дані, нові дані та доступ до пам'яті.

Структурний update ratio рахується за явним diff: added/removed/rewired
об'єкти, не лише різниця фінальних розмірів. При нульовому початковому розмірі
ratio = null; додатково завжди записується абсолютний diff.
Gate: менша повна update cost за однакової якості без неприпустимих regressions;
числові пороги, задачі, seeds і нову оцінювальну межу зафіксувати до запуску U2.

S3 дозволяється лише після відповідного позитивного C1 або L1/U2:
окремо 4/8/12-bit scaling для combinational схем, потім finite-state pattern
detector та running parity. Для sequences розділяти цілі траєкторії, а не
сусідні токени; зафіксувати reset/state semantics і перевірку послідовностей.
Toy language, FPGA, ASIC та LLM залишаються поза поточним бюджетом.
Жодна гілка не просувається до них через одну успішну XOR-демонстрацію.

## 8. Дані, seeds та звітність першої серії

Структуровані 8-bit задачі: parity всіх 8 bits; majority з порогом sum >= 4;
unsigned comparator A > B для двох 4-bit слів; MUX із 2 address bits,
4 data bits і 2 nuisance bits. Encoding/bit order фіксуються в config.
Негативний контроль: випадкова Boolean lookup function із 256 independent
bits, generator seed 93001; не пересемплювати через незручний результат.
Її unseen labels не повинні бути доступні learner. Не вимагати від неї
точно 50% accuracy на малій вибірці й не робити висновок із одного seed.

Розбиття: 128 train / 64 validation / 64 test зі всіх 256 унікальних входів,
без replacement. П'ять split seeds: 93101, 93202, 93303, 93404, 93505.
Порядок train має окремі парні seeds: 94101, 94202, 94303, 94404, 94505.
Teacher/feature seeds: 95101, 95202, 95303, 95404, 95505.
Генератор: NumPy PCG64; записати точні membership/order arrays і hashes.
Для order sensitivity фіксувати одне розбиття й змінювати тільки order у
майбутній окремій ablation; не змішувати цей ефект зі split variability.

Це development boundaries. Перекриття між п'ятьма splits означає, що їх test
не є глобально незалежним fresh confirmation після development на цих задачах.
Для сильнішої заяви потрібні нові зафіксовані task instances/domain до перегляду
їхніх результатів; просте перепризначення seeds не створює нових даних.

Звіт: per-task/per-split accuracy, RMSE, R2, nodes/depth/bytes, data access,
total synthesis/repair/verification time, peak RAM, inference median із 5 repeats
після одного warmup на validation inputs у batch 64. Час solver показувати
окремо від повного навчання. Для constant-target R2 записувати null із причиною.
Boolean accuracy використовує bits; ridge scores threshold 0.5, tie -> 0.
RMSE/R2 обчислювати на raw scores ridge та 0/1 outputs Boolean моделей.
Kernel reconstruction/rank для non-kernel схем: null/not applicable, не нуль.
Ресурсним відповідником feature budget є повний стан схеми, не кількість виходів.

Публікувати mean/sample SD та paired differences окремо для кожної задачі;
не трактувати overlapping splits як незалежні докази значущості. Для часу
додати median ratios, кількість завершених пар і всі timeout/error rows.
Не обчислювати виграш лише на зручній підмножині успішних runs.

## 9. Ресурси й умови запуску

Початкові ліміти: CPU only, один solver/BLAS thread, 4 GiB RAM на worker,
60 секунд на solver call і 300 секунд на повну model/split траєкторію,
включно з fallback та verification. V0: до 10 хвилин на suite.
C1 і L1: кожен до 4 годин послідовного wall time; фіксований порядок runs,
зупинка по бюджету із записом усіх not-run/timeout, без повторів для порятунку.
Backend build/setup не включати в inference, але записати окремо.
Це запропоновані ліміти; зміни дозволені лише до evaluation і з новою версією
протоколу. Будь-які feasibility measurements виконувати на окремих fixtures.

До активації кожного C1/L1 обов'язкові: окремий protocol + JSON config,
точні teacher/baseline grids, solver encoding/version/seed, candidate schedule,
equivalence checker, timeout policy, primary metric, числовий decision gate,
команда, source commit, environment manifest і тести data isolation.
До цього статус лишається `planned`, не `locked` і не `implemented`.

Після запуску: зберегти повний артефакт, пояснення негативних outcomes,
рішення continue/pause/closed-negative, оновити research-log та register,
закомітити й запушити. Жодних energy, novelty чи anti-monopoly claims із цих
малих експериментів. Наступний практичний артефакт нових напрямів: CS-A0 audit.
