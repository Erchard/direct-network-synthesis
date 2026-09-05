# Концептуальні засади Direct Network Synthesis

> **Статус документа:** концептуальна основа дослідницького проєкту  
> **Дата фіксації:** 2026-09-05  
> **Мова:** українська  
> **Репозиторій:** `Erchard/direct-network-synthesis`

Цей документ фіксує повну логіку, яка привела до проєкту **Direct Network Synthesis (DNS)**: від аналогій з ринком, еволюцією та інженерним проєктуванням до формальної постановки прямого, неітеративного синтезу нейронних мереж. Він навмисно зберігає **історію зміни гіпотез**, включно з невдалими ідеями, суперечностями, уточненнями та попередніми експериментальними числами.

Документ не є заявкою на новизну, не є статтею і не підміняє `docs/methodology.md`. Його мета — дати досліднику або Codex повну карту того, **чому ми взагалі прийшли до цієї задачі, що вже вважаємо правдоподібним, що спростували і що саме потрібно перевіряти далі**.

---

## 0. Як читати цей документ: рівні достовірності

Щоб не змішувати ідеї з доведеними фактами, усі твердження тут слід мислити в одному з п'яти статусів:

- **[A] Міркування / аналогія.** Концептуальний аргумент, який допомагає сформулювати задачу, але сам по собі нічого не доводить.
- **[B] Математично встановлена властивість.** Наприклад, існування closed-form розв'язку ridge regression або спектрального розкладу матриці.
- **[C] Контекст із літератури, який обговорювався в чаті.** Наприклад, ELM, random features, NTK, convex reformulations, Forward Projection. Точні бібліографічні посилання ще мають бути окремо формалізовані.
- **[D] Попередній експериментальний результат із дослідницького чату.** Це **не канонічний результат репозиторію**, поки його не відтворено кодом, конфігом, commit SHA та за протоколом `docs/methodology.md`.
- **[E] Гіпотеза / майбутній напрям.** Те, що ми хочемо перевірити.

Критично важливо: числа з категорії **[D]** не можна надалі цитувати як «результат DNS» без відтворення в репозиторії.

---

# Частина I. Звідки взялася сама ідея

## 1. Ринок як ітеративне відкриття невідомого середовища

### 1.1. Підприємець і ризик

[A] Вихідна інтуїція була економічною. Підприємець вкладає ресурси до того, як знає результат. Він може втратити гроші, час і працю. Тому великий прибуток можна частково розглядати як компенсацію за прийняту невизначеність і ризик.

Водночас було зроблено важливе уточнення: **не кожен надприбуток є нагородою за ризик**. Він може виникати через монополію, дефіцит, патент, інформаційну перевагу, регуляторні привілеї, мережевий ефект тощо. Для нашої подальшої аналогії важлива не моральна оцінка прибутку, а те, що підприємницьке рішення є **ставкою на гіпотезу про середовище**.

### 1.2. Бізнес як дослідження людських потреб

[A] Підприємець фактично висуває гіпотезу:

> людям потрібен такий товар, у такій формі, в такому місці, за такою ціною.

Люди відповідають не анкетою, а реальною купівлею або відмовою від неї. Тому продаж є не лише обміном грошей на товар, а ще й **актом вимірювання**.

Якщо позначити ціну як `p`, собівартість одиниці як `C`, а кількість покупок за цією ціною як `Q(p)`, то прибуток має вигляд:

\[
\Pi(p) = (p-C)Q(p).
\]

Проблема в тому, що продавець не знає функцію `Q(p)` наперед.

### 1.3. Нова торгова точка і пошук ціни

[A] Якщо торгова точка щойно відкрилася, продавець може поставити приблизну або навіть майже випадкову стартову ціну, а потім змінювати її, спостерігаючи продажі:

\[
p_1 \rightarrow Q_1,
\]

\[
p_2 \rightarrow Q_2,
\]

\[
p_3 \rightarrow Q_3.
\]

Його мета — не максимальна ціна і не максимальна кількість продажів, а максимізація прибутку.

У розмові слово **«справедлива ціна»** використовувалось не як моральний термін, а як приблизна назва ринково знайденої ціни. Точніше надалі говорити **ринкова**, **рівноважна** або **прибутково оптимальна для конкретного продавця** ціна — залежно від постановки.

### 1.4. Чому ціну не можна просто «порахувати» до продажів

[A] Ключова проблема: потреба покупця не є фізичною величиною, яку продавець може виміряти приладом. Навіть якщо людину запитати, скільки вона готова заплатити, її відповідь може відрізнятися від поведінки в момент реальної оплати.

Тому реальна купівля стає частиною вимірювального механізму.

Звідси перше фундаментальне спостереження:

> **Якщо релевантний стан середовища неможливо спостерігати наперед, потрібні реальні проби, які дають нову інформацію.**

---

## 2. Еволюція як ще одна ітеративна система адаптації

### 2.1. Важливе уточнення: вид не «намагається» адаптуватися

[A] У біологічній еволюції немає інженера і немає суб'єкта, який поставив мету «адаптувати вид». Коректна груба схема:

\[
\text{варіація}
\rightarrow
\text{взаємодія із середовищем}
\rightarrow
\text{різний репродуктивний успіх}
\rightarrow
\text{відбір}
\rightarrow
\text{нова варіація}.
\]

Середовище фактично перевіряє варіанти організмів. Варіанти, які в конкретних умовах залишають більше нащадків, стають поширенішими.

### 2.2. Паралель із ринком

[A] Структури схожі:

**Ринок:**

\[
\text{варіант ціни/товару}
\rightarrow
\text{реакція покупців}
\rightarrow
\text{прибуток/збиток}
\rightarrow
\text{корекція}.
\]

**Еволюція:**

\[
\text{варіант організму}
\rightarrow
\text{середовище}
\rightarrow
\text{репродуктивний успіх}
\rightarrow
\text{відбір}.
\]

В обох випадках система **не має повної моделі середовища**, тому використовує реальний світ як oracle, який відповідає на експерименти.

---

## 3. Інженерне проєктування як принципово інший режим адаптації

### 3.1. Машина для відомих умов

[A] Далі було поставлено інший приклад. Людина проєктує машину для роботи в конкретних умовах: певна маса вантажу, температура, ґрунт, тиск, навантаження, ресурс тощо.

Ми не створюємо мільярд випадкових машин, щоб 99% з них зламались і лише вдалі конструкції «вижили».

Інженер використовує модель середовища:

- механіку;
- опір матеріалів;
- термодинаміку;
- характеристики двигуна;
- коефіцієнти тертя;
- геометрію;
- симуляцію.

Величезна кількість поганих варіантів відкидається **до їх фізичного виготовлення**.

### 3.2. Ітерації не зникають повністю — вони стають дешевшими

[A] Реальне машинобудування теж не відбувається ідеально за один крок. Є CAD, симуляція, прототипи, стендові тести, краш-тести, корекції конструкції.

Але радикальна відмінність у тому, що ми можемо перенести мільйони потенційних «смертей машин» із фізичного світу в модель.

Тобто центральна величина — не просто кількість ітерацій, а **вартість отримання інформації про наслідок рішення**.

### 3.3. Ідеальний граничний випадок

[A] У граничному випадку, якщо одночасно виконуються чотири умови:

1. ми досконало знаємо стан середовища;
2. знаємо закони взаємодії системи з ним;
3. точно визначили мету;
4. маємо достатній обчислювальний ресурс,

то пошукові ітерації принципово можуть бути замінені прямим розрахунком:

\[
\text{середовище}
+
\text{закони}
+
\text{ціль}
\rightarrow
\text{розраховане рішення}.
\]

Це не означає, що не потрібна фінальна верифікація. Але **верифікація рішення** — це не те саме, що **пошук рішення через послідовні невдалі спроби**.

Ця відмінність і стала мостом до нейронних мереж.

---

# Частина II. Перенесення питання на навчання нейромереж

## 4. Стандартне навчання як адаптація параметрів

[B] У сучасній нейромережі є параметри `θ` і функція втрат `L(θ)`. Типове градієнтне оновлення:

\[
\theta_{t+1}
=
\theta_t - \eta\nabla L(\theta_t).
\]

Схема:

\[
\text{передбачення}
\rightarrow
\text{помилка}
\rightarrow
\text{градієнт}
\rightarrow
\text{оновлення параметрів}
\rightarrow
\text{нове передбачення}.
\]

[A] На дуже високому рівні це теж адаптивний цикл.

Важлива відмінність від еволюції: gradient descent отримує значно багатший зворотний сигнал. Еволюційний fitness умовно каже «цей організм був успішніший», тоді як градієнт містить локальний напрям зміни великої кількості параметрів.

Тому стандартне deep learning — це не буквально дарвінівський перебір. Але центральна схожість зберігається: **параметри не обчислюються відразу; вони проходять довгу траєкторію корекцій**.

---

## 5. Центральне запитання: чи фундаментально потрібна ця траєкторія?

[A/E] Було сформульовано питання:

> Якщо весь навчальний датасет уже є перед нами, чому ми повинні проходити мільйони кроків зміни ваг? Чи не може існувати інженерний оператор, який одразу перетворює дані та архітектуру на придатні параметри?

Стандартний режим:

\[
\theta_0
\xrightarrow{D}
\theta_1
\xrightarrow{D}
\theta_2
\xrightarrow{D}
\dots
\xrightarrow{D}
\theta_n.
\]

Шуканий режим:

\[
D \xrightarrow{F} \theta^*.
\]

де `D` — навчальний набір, а `F` — прямий синтезатор.

---

## 6. Важлива корекція: «датасет — не середовище» не пояснює необхідність ітерацій

[A] У дискусії з'явилось заперечення: датасет — лише вибірка реального середовища, а не саме середовище.

Це правильно, але **це не є аргументом на користь ітеративності**, тому що звичайне SGD/backprop має рівно те саме обмеження. Воно також бачить цей самий датасет.

Отже:

- неповнота датасету пояснює проблему generalization;
- але сама по собі **не пояснює**, чому `D` треба перечитувати через послідовність вагових оновлень.

Це було важливе логічне очищення гіпотези.

---

# Частина III. Формальна постановка Direct Network Synthesis

## 7. Що саме означає «без ітерацій»

Наш термін не повинен бути неоднозначним.

### 7.1. Заборонений тип процесу

[E] Ми хочемо уникати **ітеративного пошуку параметрів** виду:

\[
W_{t+1}=W_t+\Delta W_t,
\]

де новий стан параметрів залежить від оцінки того, наскільки добре працював попередній стан.

До забороненого класу в строгому DNS-експерименті належать:

- SGD;
- Adam;
- backpropagation як механізм багаторазового оновлення ваг;
- coordinate descent по параметрах;
- evolutionary search ваг;
- random search з feedback;
- iterative learned optimization конкретних параметрів;
- будь-який цикл «змінили параметри → виміряли loss → змінили знову».

### 7.2. Дозволений прямий розрахунок

[B] Дозволені операції, які розглядаються як **обчислення відповіді**, а не пошук через проби:

- matrix multiplication;
- розв'язання систем лінійних рівнянь;
- pseudoinverse;
- ridge solve;
- SVD;
- eigendecomposition;
- QR;
- Cholesky;
- kernel construction;
- детерміноване формування ознак;
- один або кілька проходів по даних для накопичення sufficient statistics.

Важливе уточнення: деякі чисельні бібліотеки можуть внутрішньо використовувати ітеративні numerical algorithms для eigen/SVD/solve. У концептуальному сенсі DNS ці операції все одно вважаються **прямим розв'язанням заданої математичної задачі**, якщо вони не є зовнішнім циклом оптимізації trainable parameters за loss.

---

## 8. Найпростіший доказ того, що прямі ваги іноді можливі

[B] Для лінійної least-squares / ridge задачі closed-form розв'язок відомий давно.

Для ridge regression:

\[
W^*=(X^TX+\lambda I)^{-1}X^TY.
\]

Тобто для цього класу моделей схема

\[
D\rightarrow W^*
\]

вже існує.

Отже твердження «будь-яке навчання фундаментально потребує поступових оновлень ваг» є хибним навіть на базовому рівні.

Реальна проблема починається з **нелінійного представлення**.

---

# Частина IV. Що вже існує поруч із нашою ідеєю

## 9. Related work, який формує межі задачі

> **Статус цього розділу: [C].** Це не формальна бібліографія. Тут лише фіксуються напрями, які були знайдені та обговорені. Окремий literature review має додати точні авторів, назви, DOI/arXiv і порівняльну таблицю.

### 9.1. Extreme Learning Machine (ELM)

ELM показує, що можна:

1. зафіксувати hidden representation без gradient training;
2. аналітично обчислити output weights через pseudoinverse/ridge.

Схема:

\[
H=\phi(XW_{fixed}+b),
\]

\[
\beta=H^+Y.
\]

Це принципово важливо для DNS: **нелінійна мережа може мати аналітичний readout**.

Але випадковий hidden layer не вирішує нашу глибшу задачу інженерного проєктування representation.

### 9.2. Random Features

Random features аналогічно переводять нелінійну задачу у фіксований feature space, після чого останній етап може бути лінійним closed-form solve.

### 9.3. Kernel methods і kernel ridge

Kernel ridge — ще сильніший доказ того, що **нелінійна модель може бути fitted без gradient updates параметрів нейромережі**.

Для kernel matrix `K`:

\[
\alpha=(K+\lambda I)^{-1}Y.
\]

Проблема — масштабування, оскільки типово:

\[
K\in\mathbb{R}^{N\times N}.
\]

Це зробило kernel ridge нашим майбутнім **oracle/specification**, а не кінцевим рішенням.

### 9.4. Neural Tangent Kernel (NTK)

Обговорювався погляд, де нескінченно широкі мережі в певному режимі описуються kernel dynamics, а training може аналізуватися в просторі функцій. Для DNS це важливо концептуально: межа між «мережею» та «kernel machine» не абсолютна.

### 9.5. Convex reformulations для окремих ReLU-мереж

Обговорювались роботи, де для спеціальних ReLU-постановок не-опукла training problem переписується як опукла, інколи з глобальними гарантіями.

Висновок для DNS: **архітектуру можна спеціально вибирати так, щоб задача синтезу ставала математично зручнішою**.

### 9.6. Closed-form / layer-wise learning

У літературі існують різні layer-wise методи, де частини мережі обчислюються без класичного end-to-end backprop.

### 9.7. Forward Projection (2026, обговорено в research chat)

У чаті була розглянута робота **Forward Projection**, де багатошарова мережа отримує локальні hidden targets, а ваги шарів обчислюються через closed-form regression без backpropagation.

Типова форма міжшарового solve:

\[
W_l=
(A_{l-1}^TA_{l-1}+\lambda I)^{-1}
A_{l-1}^T\tilde Z_l.
\]

Для нашої програми це надзвичайно важливо: воно показує, що **багатошаровість сама по собі не змушує використовувати backprop**.

Наша відмінна мотивація: не задовольнятися випадковими або евристичними target projections, а шукати **детерміновано спроєктовану геометрію hidden states**.

### 9.8. Hypernetworks і meta-learning

Існує інший шлях:

\[
G_\phi(D)=\theta.
\]

Тобто одна мережа приймає task/dataset і генерує параметри іншої.

Це близько до бажаного `Dataset -> Weights`, але training complexity переноситься в сам `G_φ`.

Тому hypernetwork можна розглядати як **amortized synthesis**, але не як найчистішу відповідь на початкове питання.

---

# Частина V. Головне переформулювання: проблема не у вагах, а у representation

## 10. Якщо відомі правильні hidden states, ваги можуть бути простими

[A/B] Припустимо, маємо мережу:

\[
X
\rightarrow H_1
\rightarrow H_2
\rightarrow\dots
\rightarrow H_L
\rightarrow Y.
\]

Якби хтось уже дав нам хороші target representations:

\[
H_1^*,H_2^*,\ldots,H_L^*,
\]

то міжшарові ваги в простому випадку можна шукати як regression problems:

\[
W_1 \approx X^+H_1^*,
\]

\[
W_2 \approx (H_1^*)^+H_2^*,
\]

і так далі.

З регуляризацією:

\[
W_l=
(H_{l-1}^TH_{l-1}+\lambda I)^{-1}
H_{l-1}^T H_l^*.
\]

Звідси центральне переформулювання DNS:

> **Найскладнішою частиною deep learning може бути не саме знаходження конкретних ваг, а відкриття корисної послідовності внутрішніх представлень.**

Тобто замість прямого питання

\[
D\rightarrow W
\]

може бути продуктивніше шукати:

\[
D
\rightarrow
(H_1^*,H_2^*,\ldots,H_L^*)
\rightarrow
(W_1,W_2,\ldots,W_L).
\]

---

# Частина VI. Еволюція наших власних DNS-гіпотез

## 11. DNS 0.1 — прямий спектрально-supervised hidden representation

[E] Перша практична ідея була такою:

1. взяти `X` і `Y`;
2. побудувати детерміноване приховане представлення через SVD/PCA та supervised geometry;
3. один раз розрахувати ваги до цього representation;
4. один раз розрахувати output ridge weights.

### 11.1. Попередній chat experiment

[D] На `sklearn digits` повідомлявся ранній результат близько **93.7% accuracy** для детермінованої спектральної суміші геометрії входів і міток.

Це було корисно як proof-of-life, але недостатньо конкурентно.

**Не канонізувати це число без відтворення.**

---

## 12. RBF kernel ridge як oracle

Після DNS 0.1 було поставлено більш жорстке питання: чи проблема взагалі в самій неітеративності?

[D] У ранньому чат-експерименті RBF kernel ridge на `digits` дав близько **97.96%**, тоді як контрольний невеликий MLP з backprop у тому запуску був близько **97.78%**.

Це змінило фокус:

> Нелінійна неітеративна модель може бути достатньо якісною. Проблема — зробити її компактною та масштабованою.

### 12.1. Чому в чаті з'явилося кілька різних RBF-чисел

[D] Пізніше протокол експериментів ставав суворішим, і повідомлялись інші значення:

- близько **98.06%** у одному коректнішому train/validation/test experiment;
- близько **98.61% ± 0.59** у серії 10 independent splits;
- близько **98.13%** у окремій серії нових splits;
- близько **98.19% ± 0.59** у пізнішій 20-split перевірці.

Ці числа **не треба усереднювати, вибирати найкраще або представляти як один benchmark result**. Вони відображають різні етапи експериментального дизайну.

Правильне правило:

> Канонічне число з'явиться лише після окремого committed experiment у репозиторії з зафіксованими splits, configuration, commit SHA та output artifact.

### 12.2. Спектральна компресія kernel geometry

[D] Було також перевірено, що хороша RBF kernel matrix на `digits` має значно нижчу ефективну спектральну розмірність, ніж повний `N`.

В одному ранньому аналізі повідомлялось приблизно:

| Rank | Exploratory accuracy |
|---:|---:|
| 10 | ~80.9% |
| 20 | ~89.8% |
| 50 | ~93.9% |
| 75 | ~96.1% |
| 150 | ~97.0% |
| 200 | ~97.96% |
| Full | ~97.96% |

В іншому етапі висновок формулювався ширше: **приблизно 150–300 spectral directions можуть зберігати майже всю якість RBF на цій маленькій задачі**.

Це дало ключову інтуїцію:

\[
K\approx HH^T,
\]

де `H` може бути суттєво вужчим за `N`.

Звідси виникла ідея: **мережа може бути компактним механізмом обчислення такого `H(x)`**.

---

## 13. DNS-ReLU 0.2 — детермінований ReLU feature mechanism

[E/D] Наступний прототип уже був ближчим до звичайної нейромережі.

Hidden directions будувались детерміновано з:

- PCA/SVD directions;
- напрямів між центрами класів;
- Fisher-подібних supervised directions;
- ReLU thresholds на train-derived quantiles.

Для напрямку `d_j` і порога `t_jk` ознака:

\[
h_{jk}(x)=\max(0,d_j^Tx-t_{jk}).
\]

Output weights — один ridge solve:

\[
W=(H^TH+\lambda I)^{-1}H^TY.
\]

### 13.1. Exploratory performance

[D] У різних чат-запусках повідомлялась якість приблизно **97.5–98%** на `digits` без gradient updates.

### 13.2. Важлива перевірка новизни

[C] Literature check показав, що сам принцип **PCA/LDA/Fisher-informed deterministic hidden layer + analytical output solve** не є новим. Існують PCA-ELM, LDA-ELM та інші deterministic ELM variants.

Тому DNS-ReLU 0.2 — **baseline/building block**, а не самостійний новий внесок.

Це був важливий методологічний урок: хороший benchmark result ще не означає нову ідею.

---

## 14. DNS 0.3 — наївне chaining спектральних target representations

[E] Після цього була спроба буквально реалізувати центральну гіпотезу:

\[
X
\xrightarrow{closed\ form}
H_1^*
\xrightarrow{closed\ form}
H_2^*
\xrightarrow{closed\ form}
H_3^*.
\]

За бажану геометрію брався spectral embedding хорошої kernel matrix.

### 14.1. Негативний результат

[D] Ця схема не дала достатнього покращення. У чаті згадувався найкращий validation result приблизно **96.4%** для одного з варіантів, а додавання шарів не давало систематичної переваги.

### 14.2. Діагноз

Було відкрито принципову помилку в постановці:

> **Representation може бути хорошим з точки зору задачі, але погано реалізованим конкретним попереднім шаром.**

Тобто недостатньо хотіти `T_l`. Потрібно, щоб існував практичний mapping:

\[
T_l \approx f(H_{l-1}W_l).
\]

Це привело до поняття **realizability**.

---

## 15. Realizability як другий фундаментальний критерій hidden state

[E] Хороший hidden target має одночасно задовольняти дві вимоги:

1. **Task usefulness:** бути геометрично корисним для prediction/generalization.
2. **Layer realizability:** бути досяжним з поточного representation через конкретний синтезований блок.

Тобто шукаємо не просто:

\[
H_l^*=\text{best task representation},
\]

а приблизно:

\[
H_l^*
\in
\text{TaskUseful}
\cap
\text{RealizableByLayer}_l.
\]

Це один із найважливіших conceptual shifts у всій програмі.

---

## 16. DNS 0.4 — projection of target geometry into realizable feature space

[E] Для поточного activation `A_{l-1}` детерміновано будуємо великий candidate feature space:

\[
\Phi_l=\Phi_l(A_{l-1}).
\]

Окремо будуємо бажаний target representation `T_l`.

Замість того щоб вимагати від шару буквально відтворити `T_l`, проєктуємо target у span доступних функцій:

\[
B_l=
(\Phi_l^T\Phi_l+\lambda I)^{-1}\Phi_l^TT_l,
\]

\[
H_l=\Phi_lB_l.
\]

Тепер `H_l` **за побудовою реалізований** поточним feature mechanism.

### 16.1. Realizability error

Було введено метрику:

\[
e_l=
\frac{\|T_l-H_l\|_F}{\|T_l\|_F}.
\]

Вона відповідає на питання:

> Яку частину бажаного representation цей шар фізично не здатний реалізувати?

### 16.2. Kernel-target alignment

Також використовувалась метрика типу:

\[
A(K_H,K_Y)
=
\frac{\langle K_H,K_Y\rangle_F}
{\|K_H\|_F\|K_Y\|_F}.
\]

Мета — бачити не лише accuracy, а й те, як geometry hidden space рухається в бік task structure.

### 16.3. Ранні debug observations

[D] На одному ранньому split повідомлялось:

- accuracy приблизно `96.94% -> 97.22% -> 97.50%` при 1→3 шарах;
- alignment приблизно `0.745 -> 0.930 -> 0.957`.

Це вперше дало ознаку **можливої корисної аналітичної глибини**.

Але одного split недостатньо.

### 16.4. Більш суворі multi-split перевірки

[D] На 8 нових splits повідомлявся результат приблизно:

- 1 layer: `~97.33%`;
- 3 layers: `~97.57% ± 0.51`;
- direct deterministic ReLU: `~96.91%`;
- RBF: `~98.13%`.

Після 20 нових splits картина стала тверезішою:

| Model | Exploratory mean test accuracy |
|---|---:|
| Direct deterministic ReLU | ~96.75% ± 0.85 |
| DNS 0.4, 1 layer | ~96.99% ± 0.81 |
| DNS 0.4, 2 layers | ~97.10% ± 0.79 |
| DNS 0.4, 3 layers | ~97.17% ± 0.78 |
| RBF kernel ridge | ~98.19% ± 0.59 |

### 16.5. Статистичний висновок

[D] Було оцінено, що:

- 3-layer DNS 0.4 перевищував 1-layer приблизно на **0.18 percentage points**, але `p≈0.16` — недостатньо переконливо;
- DNS 0.4 3-layer перевищував direct deterministic ReLU приблизно на **0.42 percentage points**, `p≈0.005` — виглядало значно стійкіше.

Отже ми **не прийняли** твердження «користь глибини вже доведена».

Це важлива частина професійної дисципліни проєкту: не перетворювати слабкий позитивний тренд на гучний висновок.

### 16.6. Shuffled-label sanity check

[D] При перемішаних train labels accuracy падала приблизно до **11.7%**, тобто близько до випадкових 10% для 10 класів.

Це було важливим sanity check проти очевидного label leakage.

### 16.7. Критичний негативний результат: alignment ≠ generalization

[D] Було помічено, що kernel-target alignment міг продовжувати різко зростати, наприклад приблизно:

\[
0.65\rightarrow0.84\rightarrow0.93,
\]

тоді як test accuracy зростала лише незначно:

\[
96.99\rightarrow97.10\rightarrow97.17.
\]

Звідси сильний висновок:

> **Максимізація схожості hidden geometry з label geometry не є правильною кінцевою ціллю.**

Надмірне стягування train representation до labels може покращувати train-task alignment і одночасно майже не покращувати generalization.

### 16.8. Residual/skip variant

[D] Була також перевірена residual/skip ідея, щоб наступні шари не втрачали інформацію попередніх.

Повідомлялось, що realizability error при цьому знижувався приблизно:

\[
0.19\rightarrow0.12\rightarrow0.09,
\]

але test accuracy не покращилась і в окремих development runs навіть погіршувалась.

Висновок:

> Проблема DNS 0.4 — не просто в інформаційній втраті або поганій realizability. Можна краще реалізувати неправильний target.

---

# Частина VII. DNS 0.5 — Kernel Compiler

## 17. Найсильніше переформулювання на цей момент

Після DNS 0.4 виникла проста і сильна ідея:

> **Не треба вигадувати “ідеальну” hidden geometry, якщо ми вже знаємо функціональну геометрію, яка добре працює.**

RBF kernel ridge в наших exploratory experiments стабільно був сильнішим за поточні DNS prototypes.

Тому RBF можна використовувати не як конкурента, а як **специфікацію поведінки**.

Ціль змінюється з:

\[
X,Y\rightarrow\text{вигадане }K^*
\]

на:

\[
K_{oracle}
\rightarrow
\text{compact executable neural representation}.
\]

Це і є філософія **Kernel Compiler**.

---

## 18. Kernel as specification, network as compiled mechanism

[A/E] У термінах інженерної аналогії:

- `K*` — це вже відома специфікація того, які точки мають бути близькими або далекими;
- нейромережа — компактний механізм, який має відтворити цю поведінку;
- ми не «вирощуємо» її ваги через loss trajectory;
- ми **компілюємо відому функціональну структуру в параметричний механізм**.

Це значно ближче до початкової ідеї інженерного проєктування машини для відомого середовища.

---

## 19. Базова математика DNS 0.5

Нехай сильний oracle kernel:

\[
K^*=K_{RBF}.
\]

Робимо spectral decomposition:

\[
K^*=U\Lambda U^T.
\]

Вибираємо rank `r`:

\[
T=U_r\Lambda_r^{1/2}.
\]

Тоді:

\[
TT^T\approx K^*.
\]

### 19.1. Перший блок

Будуємо детермінований realizable feature space `Φ₁(X)` і проектуємо target:

\[
B_1=(\Phi_1^T\Phi_1+\lambda I)^{-1}\Phi_1^TT,
\]

\[
H_1=\Phi_1B_1.
\]

Його kernel approximation:

\[
K^{(1)}=H_1H_1^T.
\]

### 19.2. Не повторювати весь target — вчити лише residual geometry

Обчислюємо:

\[
R_1=K^*-K^{(1)}.
\]

Оскільки residual може бути indefinite через approximation errors, беремо позитивну спектральну частину:

\[
R_1^+=U_+\Lambda_+U_+^T.
\]

Target другого блока:

\[
T_2=U_+\Lambda_+^{1/2}.
\]

Другий блок синтезується так, щоб пояснювати **лише те, що не пояснив перший**.

Після `L` блоків:

\[
K^{(L)}=\sum_{l=1}^{L}H_lH_l^T.
\]

Residual:

\[
R_L=K^*-K^{(L)}.
\]

Головна structural metric:

\[
E_L=
\frac{\|K^*-K^{(L)}\|_F}
{\|K^*\|_F}.
\]

---

## 20. Що означатиме справжня «корисна аналітична глибина»

[E] Недостатньо, щоб 3-layer network просто була складнішою.

Ми хочемо одночасно бачити:

\[
E_1>E_2>E_3>\dots
\]

і бажано:

\[
Acc_1\le Acc_2\le Acc_3\le\dots
\]

Тобто кожен новий **closed-form synthesized block** повинен:

1. пояснювати нову частину oracle geometry;
2. не руйнувати попередню;
3. бажано давати generalization gain.

Якщо reconstruction error зменшується, але accuracy не змінюється, це теж інформативно: можливо, ми компілюємо частини kernel, які не важливі для downstream decision boundary.

Якщо accuracy зростає без monotonic kernel reconstruction — можливо, reconstruction metric не відповідає task-relevant geometry.

---

# Частина VIII. Теоретичні обмеження і правильна амбіція

## 21. Чому не варто шукати універсальну магічну формулу для довільної мережі

[C] У дискусії були розглянуті complexity-theory results, за якими training навіть відносно малих ReLU networks у загальному випадку може бути computationally hard, а ширші постановки мають дуже високу алгебраїчну складність.

Для нас це не доказ неможливості DNS.

Навпаки, це підказує **правильний тип задачі**:

Не:

\[
F(\text{arbitrary architecture},D)=\text{global optimal arbitrary weights}.
\]

А:

> **Спроєктувати спеціальний клас synthesis-friendly architectures, для яких прямий розрахунок є частиною самої конструкції.**

Це аналогічно інженерії: механізми часто проєктують так, щоб їх можна було розраховувати, аналізувати, модульно збирати і перевіряти.

---

## 22. Synthesis-friendly network як окремий об'єкт дослідження

[E] Майбутня архітектура DNS не зобов'язана бути стандартним MLP або стандартним Transformer.

Можливі принципи:

- кожен блок має явно визначений feature basis;
- кожен блок має closed-form projection/readout;
- residual decomposition гарантує модульну користь;
- representation має контрольований rank;
- geometry кожного блока вимірюється;
- міжшарові mappings допускають stable linear algebra solve;
- архітектура створюється **під синтез**, а не під backprop.

Це може бути важливішим за спробу «навчити стандартну архітектуру іншим методом».

---

# Частина IX. Методологічні стандарти

## 23. Чому цей проєкт легко випадково обманути

DNS-дослідження особливо вразливе до self-deception, тому що:

- можна підібрати kernel до test;
- можна підібрати rank після перегляду test accuracy;
- можна вибрати «гарний» random split;
- можна порівнювати зі слабким MLP;
- можна назвати старий ELM-підхід новим;
- можна непомітно внести iterative optimization у feature selection;
- можна показати лише позитивні variants;
- можна використати labels у preprocessing, який торкається test data.

Тому protocol — частина самого наукового внеску.

---

## 24. Обов'язкові правила експерименту

Цей розділ узгоджується з `docs/methodology.md`.

### 24.1. Train / validation / test

- Train — для fitting preprocessing, kernel statistics, feature synthesis, closed-form coefficients.
- Validation — для model selection і hyperparameters.
- Test — лише для final locked comparison.

Після перегляду test metrics не можна змінювати метод і продовжувати називати той самий test «небаченим».

### 24.2. Seeds

Фіксуються:

- split seeds;
- sampling seeds;
- будь-яка pseudo-random feature generation;
- synthetic dataset seeds.

### 24.3. Multiple splits

Single split — debugging only.

Для evidence потрібні:

- mean;
- standard deviation;
- paired comparisons, де можливо;
- effect size;
- confidence interval або statistical test, якщо робиться claim про improvement.

### 24.4. Leakage checks

Мінімум:

- shuffled-label sanity test;
- preprocessing fit only on train;
- kernel hyperparameters selected without test;
- no test-derived thresholds;
- no split cherry-picking.

### 24.5. Ablations

Для кожного нового компонента треба вміти прибрати його і показати, що змінюється.

Для DNS 0.5 це, наприклад:

- no residual blocks;
- random spectral targets;
- PCA-only feature basis;
- Fisher-only;
- no positive-residual clipping;
- fixed rank vs adaptive rank;
- different oracle kernels;
- same total feature budget in 1 block vs several blocks.

### 24.6. Negative results are first-class results

Якщо DNS 0.5 не дає useful depth — це не «невдалий запуск, який треба приховати». Це відповідь на конкретну гіпотезу.

`docs/research-log.md` повинен містити і відкинуті варіанти.

### 24.7. No novelty claims without related-work comparison

Будь-який механізм має спочатку порівнюватися з:

- ELM family;
- deterministic ELM;
- PCA/LDA/Fisher feature networks;
- kernel approximation;
- Nyström/random features;
- closed-form layer-wise literature;
- Forward Projection-like methods;
- distillation/kernel-to-network related methods.

---

# Частина X. Критерії успіху

## 25. Stage 1 — довести якісний direct nonlinear fitting

Це вже conceptually не є головною невідомою, тому що kernel ridge та fixed-feature methods показують, що таке можливо.

Але в репозиторії все одно потрібен reproducible baseline.

Критерій:

- closed-form nonlinear model;
- clean split protocol;
- competitive with simple gradient-trained baseline;
- no hidden test tuning.

---

## 26. Stage 2 — довести compactness

Kernel oracle сам по собі не є кінцевою перемогою через `O(N^2)` storage/compute.

Потрібно показати:

\[
K^*\approx HH^T,
\]

де width `r << N` і inference для нового `x` не потребує порівняння з усім training set.

---

## 27. Stage 3 — довести useful analytic depth

Це один із найважливіших критеріїв.

Потрібно порівняти за однакового feature/parameter budget:

- one-block compiled model;
- two-block residual compiled model;
- three-block residual compiled model.

Справжній evidence of depth:

1. кожен блок має незалежно вимірюваний residual contribution;
2. reconstruction error падає;
3. generalization не деградує;
4. багатоблокова структура стабільно краща за еквівалентний one-shot basis.

Якщо останнього немає, ми маємо просто additive feature expansion, а не доказ корисної глибини.

---

## 28. Stage 4 — масштабування без квадратної залежності від N

DNS має сенс як альтернативна paradigm лише якщо kernel specification можна отримувати або апроксимувати без materialization повної `N x N` matrix.

Майбутні можливі напрямки:

- blockwise Gram computation;
- low-rank Nyström-like statistics;
- structured kernels;
- landmark selection без iterative task optimization;
- streaming covariance/kernel statistics;
- hierarchical spectral decomposition.

Це поки [E].

---

# Частина XI. Roadmap масштабування

## 29. Етапи задач

### 29.1. `sklearn digits`

Мета: швидка лабораторія для математичних ablations.

Не використовувати як доказ масштабованості.

### 29.2. MNIST / Fashion-MNIST

Перехід лише після того, як:

- DNS 0.5 стабільно відтворюється;
- є locked protocol;
- є residual-block ablation;
- зрозуміла memory complexity.

### 29.3. CIFAR-10 / CIFAR-100

Це перший серйозний тест того, чи representation synthesis працює на більш складній візуальній геометрії.

Тут, можливо, потрібні convolutional або local structured feature bases.

### 29.4. Larger vision

Тільки після доказу, що kernel compiler не розвалюється за `N` і dimensionality.

### 29.5. Small Transformer

Перший language-model experiment має бути маленьким і контрольованим.

### 29.6. Autoregressive language modeling

Лише після того, як ми маємо evidence, що multi-layer direct synthesis реально створює корисну hierarchy, а не просто fixed-feature classifier.

---

# Частина XII. Спекулятивний напрям для Transformer

## 30. Top-down design of hidden representations

[E] Для next-token prediction dataset уже задає пари:

\[
(x_1,\ldots,x_t)\rightarrow x_{t+1}.
\]

Одна з ідей — не будувати representations лише forward, а **спроєктувати target hierarchy зверху вниз**.

Наприклад:

1. сформувати representation, де next-token readout простий;
2. побудувати попередній target, який містить більше інформації про context, але легко трансформується в наступний;
3. продовжити назад до input representation;
4. після цього аналітично синтезувати forward mappings.

Схематично target design:

\[
Y
\rightarrow T_L
\rightarrow T_{L-1}
\rightarrow\dots
\rightarrow T_1,
\]

а implementation:

\[
X
\rightarrow T_1
\rightarrow T_2
\rightarrow\dots
\rightarrow T_L
\rightarrow Y.
\]

Це поки чиста гіпотеза. DNS 0.5 має дати простіший test-bed для перевірки самого принципу «representation first, weights second».

---

# Частина XIII. Чому GitHub і Codex стали потрібними саме зараз

## 31. Перехід від розмови до research codebase

На початку ідеї можна було обговорювати в чаті. Але після появи:

- DNS versions;
- multi-split results;
- p-values;
- negative variants;
- configuration dependence;
- literature overlap;

чат перестає бути достатнім носієм наукової пам'яті.

Версійний репозиторій потрібен для:

- exact code history;
- configs;
- reproducible commands;
- fixed experiment IDs;
- curated result summaries;
- negative result log;
- зв'язку між hypothesis change і commit.

`docs/hypothesis.md` має залишатися коротким формальним statement.

`docs/methodology.md` — нормативним protocol.

`docs/research-log.md` — chronological lab notebook.

Цей файл — **повна conceptual memory**.

---

# Частина XIV. Хронологія зміни гіпотез

## 32. Timeline / hypothesis evolution

| Етап | Початкова думка | Що її змінило | Новий висновок |
|---|---|---|---|
| Ринок | Правильна ціна відкривається через проби | Потреби людей не можна напряму виміряти до реальної покупки | Ітерації потрібні, коли експеримент створює нову інформацію |
| Еволюція | Адаптація потребує варіацій і відбору | Немає моделі середовища, є лише feedback виживання | Відбір — спосіб пошуку без повної моделі |
| Інженерія | Можна зменшити проби | Відомі умови + фізичні закони дозволяють розрахунок | За достатнього знання search може бути замінений synthesis |
| NN training | SGD — нормальний спосіб навчання | Dataset уже доступний до першого update | Треба спитати, чи weight trajectory фундаментально необхідна |
| Dataset objection | Dataset не є середовищем | SGD бачить той самий dataset | Це проблема generalization, але не аргумент за iteration |
| DNS 0.1 | Синтезувати `H` спектрально | ~93.7% exploratory quality | Проста spectral mixture недостатня |
| Kernel baseline | Можливо, nonlinear closed-form слабкий | RBF ~98% exploratory | Неітеративність не є головною перешкодою; scaling є |
| DNS-ReLU 0.2 | Deterministic ReLU directions можуть вирішити задачу | ~97.5–98%; literature overlap | Працює, але близьке до known deterministic ELM family |
| DNS 0.3 | Достатньо вибрати хороший target `H` | Chained targets не дали depth gain | Task-good representation може бути unrealizable |
| Realizability | Потрібен target, який шар здатен реалізувати | Projection method працює стабільніше | Шукати intersection task-useful × realizable |
| DNS 0.4 | Alignment до labels має рости по шарах | Alignment росте сильніше, ніж test accuracy; residual не рятує | Label alignment не є objective generalization |
| DNS 0.5 | Треба знайти кращу target geometry | RBF already gives good geometry | Не винаходити geometry; компілювати oracle kernel |
| Поточний етап | Kernel reconstruction може породити useful depth | Ще не перевірено | Наступний експеримент — residual Kernel Compiler |

---

# Частина XV. Що ми зараз вважаємо найбільш правдоподібним

## 33. What we currently believe

Нижче — не «доведені істини», а поточні робочі переконання, сформовані аргументами та exploratory evidence.

### 33.1. Ітеративне weight training не є універсально необхідним

[B/C/D] Існують linear closed-form methods, kernel ridge, ELM-like models і layer-wise closed-form approaches. Тому сам факт нелінійності або наявності hidden layer не робить gradient updates логічно неминучими.

### 33.2. Hidden representation — центральніша проблема, ніж output weights

[A/D] Output ridge solve зазвичай простий. Найбільша невідомість — як отримати компактне representation, яке одночасно:

- містить task-relevant structure;
- generalizes;
- реалізується synthesis-friendly architecture;
- масштабується.

### 33.3. Task alignment alone недостатній

[D] Високий label alignment може рости без відповідного generalization gain.

### 33.4. Realizability alone теж недостатня

[D] Residual/skip experiments показали, що навіть зменшення target reconstruction error не гарантує кращої test accuracy.

### 33.5. Strong known kernel — краща початкова специфікація, ніж вигаданий target

[A/D/E] Якщо RBF consistently stronger, раціонально спочатку навчитися **компілювати його поведінку**, а вже потім шукати складніші task-specific geometries.

### 33.6. Architecture should be designed for synthesis

[C/E] Universal direct training arbitrary networks, імовірно, не є правильною першою ціллю. Потрібен окремий клас networks/blocks, де analytical synthesis є architectural primitive.

---

# Частина XVI. Що досі не доведено

## 34. What is still unproven

1. **Не доведено, що DNS 0.5 реально дає useful depth.**
2. **Не доведено, що kernel compiler може match RBF accuracy компактною мережею.**
3. **Не доведено, що reconstruction `K*` — правильний objective для generalization.**
4. **Не доведено, що multi-block residual compilation кращий за one-shot feature expansion того самого total width.**
5. **Не доведено scalability beyond toy datasets.**
6. **Не доведено, що метод працює на high-dimensional raw images без hand-designed local structure.**
7. **Не доведено, що representation synthesis переноситься на sequence models.**
8. **Не доведено, що direct synthesis може бути computationally cheaper за SGD при однаковій якості на великих задачах.**
9. **Не доведено novelty жодної поточної формули.**
10. **Не доведено, що саме “неітеративність” буде практичною перевагою, а не просто іншим tradeoff compute/memory.**
11. **Не доведено, що потрібен буквально один pass по dataset.** Наша основна вимога зараз — відсутність iterative parameter search, а не fetishization одного physical pass.

---

# Частина XVII. Immediate next experiment: DNS 0.5 Kernel Compiler

## 35. Мета експерименту

Перевірити вузьке твердження:

> **Чи може послідовність детермінованих closed-form blocks дедалі краще апроксимувати сильну RBF geometry і чи дає ця residual compilation стабільну перевагу над one-shot feature model за порівнянного бюджету?**

Не намагатися одночасно довести scalability, novelty і superiority to deep learning.

---

## 36. Dataset і protocol

Перший canonical experiment:

- `sklearn digits`;
- stratified train/validation/test splits;
- fixed list of split seeds;
- no test tuning;
- all hyperparameters selected before locked test run;
- run ID + commit SHA + config saved.

Classification metrics:

- accuracy;
- optionally log-loss/calibration if readout supports it;
- mean ± std across splits;
- paired delta vs baselines;
- confidence interval / paired test for primary comparisons.

Structural metrics:

- kernel reconstruction error `E_L`;
- spectral energy captured;
- rank/width per block;
- total feature count;
- memory footprint;
- solve time;
- inference time;
- optional alignment metrics, але не як primary optimization target.

---

## 37. Oracle definition

Побудувати RBF kernel тільки з train data:

\[
K^*_{ij}=\exp(-\gamma\|x_i-x_j\|^2).
\]

`γ` вибирається лише через train/validation protocol.

Canonical RBF kernel ridge performance записується як oracle reference.

---

## 38. Spectral target

Розкласти:

\[
K^*=U\Lambda U^T.
\]

Вибрати rank `r` на validation або за train-only spectral energy rule, зафіксованим до test.

Target:

\[
T_1=U_r\Lambda_r^{1/2}.
\]

---

## 39. Block 1 synthesis

Створити `Φ₁(X)` з детермінованого feature generator.

Перші candidate families:

- PCA directions + quantile ReLU knots;
- PCA + class-centroid directions;
- PCA + Fisher directions;
- possibly structured polynomial/RBF-like deterministic features.

Projection:

\[
B_1=(\Phi_1^T\Phi_1+\lambda I)^{-1}\Phi_1^TT_1,
\]

\[
H_1=\Phi_1B_1.
\]

---

## 40. Residual kernel decomposition

\[
R_1=K^*-H_1H_1^T.
\]

Symmetrize numerically if needed:

\[
R_1\leftarrow\frac{R_1+R_1^T}{2}.
\]

Take positive spectral component:

\[
R_1^+=U_+\Lambda_+U_+^T.
\]

Target next block:

\[
T_2=U_{+,r_2}\Lambda_{+,r_2}^{1/2}.
\]

Repeat for block 2/3.

---

## 41. Critical comparison: depth versus width

Це обов'язкова ablation.

Порівняти:

### A. One-shot wide

Один `Φ` з total width `M`.

### B. Residual multi-block

Наприклад 3 blocks по width `M/3`.

Якщо B не перевищує A, то multi-block structure може бути лише складнішим способом створення того самого feature budget.

Evidence for useful depth існує лише якщо multi-block residual organization дає стабільну перевагу при fair budget.

---

## 42. Additional ablations

1. `RBF oracle` vs `linear kernel oracle`.
2. Full target every layer vs residual target.
3. Positive spectral residual vs raw residual approximation.
4. PCA-only `Φ` vs PCA+Fisher.
5. Fixed equal rank per block vs residual-energy adaptive rank.
6. `H_l` concatenation vs additive kernel sum only.
7. One-shot low-rank RBF features vs compiled ReLU mechanism.
8. Oracle spectral embedding readout as upper bound.

---

## 43. Failure criteria

DNS 0.5 вважається **невдалим у поточній формі**, якщо після fair tuning на validation:

- residual blocks не зменшують `E_L`;
- або `E_L` падає, але test accuracy систематично не покращується;
- або one-shot wide baseline стабільно не гірший;
- або compiled model потребує майже `N` hidden dimensions;
- або inference фактично зберігає dependency на весь train set;
- або method relies on test-derived information;
- або advantage disappears across independent splits.

Негативний результат не закриває DNS program — він лише спростовує конкретний compiler design.

---

## 44. Що буде достатнім позитивним сигналом

На `digits` ми не потребуємо «нового state of the art».

Сильний first-stage success:

1. DNS 0.5 має no iterative parameter optimization.
2. 2–3 residual blocks monotonically reduce kernel error.
3. Multi-block model statistically beats fair one-block model за того самого budget.
4. Test accuracy підходить близько до locked RBF oracle.
5. Hidden representation суттєво менший за `N`.
6. Повторюється на independent splits.

Після цього є сенс переходити до MNIST/Fashion-MNIST.

---

# Частина XVIII. Глосарій символів

## 45. Symbols

| Symbol | Meaning |
|---|---|
| `D` | Повний dataset / навчальна задача |
| `X` | Input matrix / features |
| `Y` | Targets / labels |
| `θ` | Загальний вектор параметрів моделі |
| `W_l` | Ваги шару `l` |
| `H_l` | Реалізоване hidden representation шару `l` |
| `H_l*` | Бажане / ідеальне hidden representation |
| `A_l` | Activations шару `l` |
| `Φ_l` | Candidate feature matrix / realizable feature space для блока `l` |
| `T_l` | Target representation для блока `l` |
| `B_l` | Closed-form projection coefficients з `Φ_l` у `T_l` |
| `K` | Kernel / Gram matrix |
| `K*` | Oracle або target kernel |
| `K^(L)` | Kernel approximation після `L` compiled blocks |
| `R_l` | Residual kernel після блока `l` |
| `U, Λ` | Eigenvectors та eigenvalues spectral decomposition |
| `r` | Rank / target embedding width |
| `λ` | Ridge regularization coefficient |
| `γ` | RBF kernel bandwidth parameter у формі `exp(-γ||x-x'||²)` |
| `Q(p)` | Кількість покупок як функція ціни в економічній аналогії |
| `Π(p)` | Прибуток продавця |
| `E_L` | Relative kernel reconstruction error після `L` blocks |
| `A(K_H,K_Y)` | Kernel-target alignment |
| `e_l` | Realizability error target representation шару |

---

# Частина XIX. Коротка формула всієї програми

## 46. Від початкової інтуїції до поточної гіпотези

Початковий логічний ланцюг:

\[
\text{незнане середовище}
\Rightarrow
\text{потрібні реальні проби}
\]

\[
\text{відоме середовище + модель}
\Rightarrow
\text{можна замінювати пошук розрахунком}
\]

\[
\text{training dataset уже відомий}
\Rightarrow
\text{варто перевірити direct synthesis}
\]

Після всіх уточнень поточна research program виглядає так:

\[
D
\rightarrow
\text{task/oracle geometry}
\rightarrow
\text{compact realizable representations}
\rightarrow
\text{closed-form block parameters}
\rightarrow
\text{compiled network}.
\]

Для DNS 0.5:

\[
K^*_{RBF}
\rightarrow
\text{spectral targets}
\rightarrow
\text{residual realizable blocks}
\rightarrow
\sum_l H_lH_l^T\approx K^*.
\]

Найважливіше питання зараз не:

> «Чи можна один раз порахувати якусь нейромережу без SGD?»

Для малих і спеціальних випадків відповідь уже очевидно «так».

Справжнє питання:

> **Чи можна створити масштабований клас нейронних систем, у яких корисна глибока внутрішня структура проєктується і компілюється прямими математичними операціями замість того, щоб відкриватися через довгу траєкторію gradient-based adaptation?**

Саме це є довгостроковою метою Direct Network Synthesis.

---

# Частина XX. TODO для наукової зрілості документації

## 47. Bibliography TODO

Окремим кроком потрібно створити `docs/related-work.md` з точною перевіреною бібліографією для напрямів, згаданих у research chat:

- closed-form linear / ridge regression;
- Extreme Learning Machine;
- deterministic / PCA / LDA ELM variants;
- random features;
- kernel ridge and low-rank kernel approximations;
- Neural Tangent Kernel;
- convex reformulations of ReLU training;
- closed-form deep/layer-wise learning;
- Forward Projection (2026);
- kernel mean embedding layer-wise networks;
- hypernetworks and dataset-to-weights meta-learning;
- kernel distillation / kernel-to-network compression;
- Nyström and spectral approximation methods.

Не додавати випадкові або неперевірені citations. Кожен related-work claim має бути прив'язаний до первинного джерела.

## 48. Experimental canonicalization TODO

Усі числа, позначені в цьому документі як **[D]**, повинні пройти через canonical experiment pipeline.

Після відтворення:

- записати command;
- config;
- commit SHA;
- split seeds;
- result artifact;
- summary table;
- confidence intervals/statistical comparison;
- і лише тоді переносити число з «exploratory chat result» у «repository result».

---

## 49. Фінальний принцип

Проєкт DNS не повинен доводити початкову інтуїцію будь-якою ціною.

Його задача — **чесно перевірити**, де проходить межа між:

- інформацією, яку справді треба отримувати через adaptive search;
- і структурою, яку можна вивести з уже доступних даних та скомпілювати прямим розрахунком.

Якщо виявиться, що певні класи deep representation фундаментально потребують adaptive optimization — це теж цінний результат.

Якщо ж виявиться, що значну частину сучасного training можна замінити прямим synthesis pipeline, тоді ми отримаємо не просто швидший optimizer, а **іншу парадигму побудови нейронних систем**.
