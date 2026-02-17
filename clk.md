# شرح الـ Common Clock Framework 🕐

## إيه هو الموضوع ده أصلاً؟

تخيل إن الـ **SoC** (الشريحة) اللي في موبايلك أو في الـ board بتاعك زي مدينة كبيرة فيها مصانع كتير (peripherals زي USB, I2C, SPI). كل مصنع ده محتاج كهربا عشان يشتغل، صح؟

الـ **clock** في الإلكترونيات زي الكهربا دي بالظبط! كل **peripheral** محتاج **clock signal** عشان يشتغل - يعني إشارة بتنبض بسرعة معينة (زي tick-tock-tick-tock) عشان الدوائر تشتغل.

---

## ليه محتاجين الـ Framework ده؟

### المشكلة 🤔
قبل كده، كل **platform** (يعني كل شركة زي STM أو NXP أو Rockchip) كانت بتعمل الكود بتاعها بطريقتها الخاصة. يعني **code duplication** كتير جداً!

### الحل ✅
الـ **Common Clock Framework** جاء يقول: "يلا كلنا نستخدم نفس الطريقة!"

يعني بدل ما كل واحد يعمل العجلة من الأول، نعمل **standard interface** واحد للكل.

---

## إزاي الـ Framework ده شغال؟

### مقسوم لنصين (Two Halves):

#### **النص الأول: الـ Common Core** 🏛️
ده موجود في `drivers/clk/clk.c` وفيه:
- **struct clk_core**: البنية الأساسية اللي فيها معلومات عن الـ clock
  - اسم الـ clock
  - مين الـ **parent** بتاعه (الأب)
  - السرعة (rate)
  - عداد كام مرة اتشغل (enable_count)

تخيله زي **مدير المصنع** - بيمسك السجلات والحسابات.

#### **النص التاني: الـ Hardware-Specific** ⚙️
ده الكود اللي **انت** هتكتبه لـ platform بتاعك! فيه:
- **struct clk_ops**: مجموعة functions عشان تتحكم في الـ hardware الحقيقي
  - `.enable`: شغّل الـ clock
  - `.disable`: قفل الـ clock
  - `.set_rate`: غيّر السرعة
  - `.set_parent`: غيّر الأب

تخيله زي **العمال** اللي بيشتغلوا في المصنع فعلاً.

---

## مثال بسيط: إزاي تشغّل Clock؟

### 1. الـ Driver بيقول:
```c
clk_enable(clk);  // يا كود، شغّل الـ clock ده!
```

### 2. الـ Framework بيعمل:
```
clk_enable() → يدوّر على الـ ops المناسبة
  ↓
clk_gate_enable() → ده الكود بتاعك اللي بيشتغل الـ hardware
  ↓
clk_gate_set_bit() → بيروح يكتب في الـ register ويقلب الـ bit
```

تخيلها زي لما بتضغط على **مفتاح الكهربا** (enable)، الكهربا بتوصل للمصباح (hardware)!

---

## الـ Structures المهمة

### **struct clk_core** (المدير)
```c
struct clk_core {
    const char *name;           // اسم الـ clock (مثلاً "usb_clk")
    struct clk_core *parent;    // مين الأب؟
    unsigned long rate;         // السرعة (frequency)
    struct clk_ops *ops;        // الـ functions بتاعتك
};
```

### **struct clk_ops** (التعليمات)
```c
struct clk_ops {
    int (*enable)(struct clk_hw *hw);      // شغّل
    void (*disable)(struct clk_hw *hw);    // قفل
    unsigned long (*recalc_rate)(...);     // احسب السرعة
    int (*set_rate)(...);                  // غيّر السرعة
    int (*set_parent)(...);                // غيّر الأب
};
```

---

## الـ Locking (الأقفال) 🔒

عشان ما يحصلش **race condition** (اتنين يشتغلوا على نفس الـ clock في نفس الوقت)، فيه نوعين أقفال:

### 1. **Enable Lock** (Spinlock) 🏃
- **سريع جداً**
- يُستخدم مع `.enable` و `.disable`
- **ممنوع النوم** (can't sleep) داخله!
- تقدر تستخدمه في **atomic context**

تخيله زي قفل بسيط بتلفه بسرعة.

### 2. **Prepare Lock** (Mutex) 😴
- **يسمح بالنوم**
- يُستخدم مع باقي العمليات (set_rate, set_parent...)
- **لازم يكون في process context**

تخيله زي قفل أكبر ممكن تستنى عنده.

---

## ليه فيه Enable و Prepare؟

### **Prepare** (التحضير):
- بيجهز الـ clock (مثلاً يشغل الـ PLL)
- **ممكن ياخد وقت** (microseconds أو milliseconds)
- ممكن ينام

### **Enable** (التشغيل الفعلي):
- بيشغل الـ clock بسرعة
- **لازم يكون سريع جداً** (nanoseconds)
- **ممنوع ينام**!

تخيلها زي السيارة:
- **Prepare** = تسخين المحرك (ياخد وقت)
- **Enable** = تشغيل السيارة فعلياً (سريع)

---

## Power Management (توفير الطاقة) ⚡

### الفكرة:
لو في **peripheral** مش شغال، ليه نسيب الـ clock بتاعه شغال ويستهلك بطارية؟

### الحل:
```c
// لما تخلص شغل
clk_disable(clk);      // اقفل الـ clock
clk_unprepare(clk);    // اطفي الـ PLL كمان

// لما تحتاجه تاني
clk_prepare(clk);      // سخّن الـ PLL
clk_enable(clk);       // شغّل الـ clock
```

كده بتوفر طاقة! 💪

---

## إزاي تعمل Driver لـ Clock بتاعك؟

### 1. عرّف الـ Structure بتاعتك:
```c
struct clk_foo {
    struct clk_hw hw;           // لازم يكون موجود!
    void __iomem *reg;          // مكان الـ register
    u8 bit_idx;                 // رقم الـ bit
};
```

### 2. اكتب الـ Operations:
```c
struct clk_ops clk_foo_ops = {
    .enable  = &clk_foo_enable,
    .disable = &clk_foo_disable,
    .set_rate = &clk_foo_set_rate,
};
```

### 3. نفّذ الـ Functions:
```c
int clk_foo_enable(struct clk_hw *hw) {
    struct clk_foo *foo = to_clk_foo(hw);

    // اكتب في الـ register
    u32 reg = readl(foo->reg);
    reg |= BIT(foo->bit_idx);  // قلب الـ bit
    writel(reg, foo->reg);

    return 0;
}
```

### 4. سجّل الـ Clock:
```c
clk_register(...);  // قول للـ kernel: عندي clock جديد!
```

---

## الخلاصة 🎯

الـ **Common Clock Framework** هو:
- **مدير موحّد** لكل الـ clocks في النظام
- بيوفر **interface** سهل للـ drivers
- بيساعد في **power management**
- **مقسوم لنصين**: common code + hardware-specific code
- فيه **two-phase locking** (prepare/enable) عشان الكفاءة

تخيل الـ kernel زي مدينة فيها **مولد كهربا رئيسي** (root clock) و**محطات فرعية** (derived clocks)، والـ framework ده هو **لوحة التحكم** اللي بتتحكم في كل حاجة! 🏗️

---

# شرح أعمق للـ Common Clock Framework 🔍

## 1. الـ Clock Tree (شجرة الـ Clocks) 🌳

### تخيل الموضوع كده:

عندك **مولد كهربا رئيسي** (crystal oscillator) بيدي 24 MHz. منه بيتفرع كل حاجة في النظام.

```
                    Crystal (24 MHz)
                          |
                    +-----+-----+
                    |           |
                  PLL1        PLL2
                (800 MHz)   (600 MHz)
                    |           |
            +-------+-------+   +-------+
            |       |       |           |
         CPU_CLK  AHB_CLK APB_CLK    USB_CLK
        (400MHz) (200MHz) (100MHz)   (48MHz)
            |       |        |           |
          [CPU]  [DMA]   [UART]       [USB]
```

كل **clock** ليه **parent** (أب)، والأب ده بييجي منه الإشارة الأصلية.

---

## 2. الـ Parent-Child Relationship (علاقة الأب والابن)

### ليه مهمة؟

لو غيّرت سرعة **الأب**، لازم **الابن** يحسب سرعته تاني!

### مثال من الحياة الواقعية:

```c
struct clk_core {
    struct clk_core *parent;        // مين الأب؟
    struct clk_core **parents;      // لو عندي أكتر من أب محتمل
    u8 num_parents;                 // عدد الآباء المحتملين
    const char **parent_names;      // أسماء الآباء
};
```

**ليه أكتر من parent محتمل؟** 🤔

لأن بعض الـ clocks بتقدر **تختار** مصدرها! زي **multiplexer**:

```
      PLL1 ----\
                 \
      PLL2 -------> [MUX] ----> USB_CLK
                 /
      Crystal --/
```

الـ driver يقدر يقول: "عايز USB_CLK ييجي من PLL1 النهارده" عن طريق:
```c
clk_set_parent(usb_clk, pll1);
```

---

## 3. أنواع الـ Clocks المختلفة

### أ) **Fixed Rate Clock** (سرعة ثابتة) 🔒

أبسط نوع! زي الـ **crystal oscillator**.

```c
struct clk_fixed_rate {
    struct clk_hw hw;
    unsigned long fixed_rate;  // السرعة الثابتة (مثلاً 24000000)
    unsigned long flags;
};
```

**مافيش** set_rate ولا حاجة، السرعة ثابتة للأبد!

#### مثال:
```c
// Crystal 24 MHz
clk_register_fixed_rate(NULL, "osc24M", NULL, 0, 24000000);
```

---

### ب) **Gate Clock** (بوابة تشغيل/إيقاف) 🚪

بيشغل ويقفل الـ clock بس، **مابيغيرش السرعة**.

```c
struct clk_gate {
    struct clk_hw hw;
    void __iomem *reg;      // عنوان الـ register
    u8 bit_idx;             // رقم الـ bit اللي بيتحكم
    u8 flags;
    spinlock_t *lock;
};
```

#### إزاي بيشتغل؟

```c
static int clk_gate_enable(struct clk_hw *hw) {
    struct clk_gate *gate = to_clk_gate(hw);
    u32 val;

    // اقرا الـ register الحالي
    val = readl(gate->reg);

    // قلّب الـ bit المطلوب لـ 1
    val |= BIT(gate->bit_idx);

    // اكتب القيمة الجديدة
    writel(val, gate->reg);

    return 0;
}
```

**في الـ hardware:**
```
Register: 0x12340000
Bits:     [31....8][7][6][5][4][3][2][1][0]
                    ^
                    |
               USB clock gate (bit 7)

عايز تشغل USB؟ اكتب 1 في bit 7
عايز تقفله؟ اكتب 0 في bit 7
```

---

### ج) **Divider Clock** (مقسّم السرعة) ➗

بياخد clock من الأب **ويقسمه**!

```c
struct clk_divider {
    struct clk_hw hw;
    void __iomem *reg;
    u8 shift;           // من فين يبدأ في الـ register
    u8 width;           // كام bit للـ divider
    u8 flags;
    const struct clk_div_table *table;  // جدول القسمة
    spinlock_t *lock;
};
```

#### مثال:
```
Parent = 800 MHz
Divider = 4
Result = 800 / 4 = 200 MHz
```

#### في الـ hardware:
```
Register: 0x12340010
Bits [2:0] = divider value
  000 = divide by 1
  001 = divide by 2
  010 = divide by 4
  011 = divide by 8
  ...
```

```c
// عايز 200 MHz من 800 MHz؟
// يعني divider = 4
// يعني bits = 010
writel(0x2, divider_reg);
```

---

### د) **Mux Clock** (المُبدِّل) 🔀

بيختار **من مين** ييجي الـ clock!

```c
struct clk_mux {
    struct clk_hw hw;
    void __iomem *reg;
    u32 *table;         // جدول المصادر
    u32 mask;
    u8 shift;
    u8 flags;
    spinlock_t *lock;
};
```

#### مثال:
```
Sources:
  00 = Crystal (24 MHz)
  01 = PLL1 (800 MHz)
  10 = PLL2 (600 MHz)
  11 = Reserved

عايز تختار PLL1؟ اكتب 01 في الـ bits المخصصة
```

---

### هـ) **PLL Clock** (أهم نوع!) ⚙️

الـ **Phase-Locked Loop** - ده اللي بيضاعف السرعة!

```c
struct clk_pll {
    struct clk_hw hw;
    void __iomem *pll_base;
    u32 m;      // Multiplier (المضاعف)
    u32 n;      // Divider (المقسم)
    u32 p;      // Post divider (مقسم إضافي)
};
```

#### المعادلة السحرية:
```
Output = (Input × M) / (N × P)

مثال:
Input = 24 MHz
M = 100
N = 3
P = 2

Output = (24 × 100) / (3 × 2) = 2400 / 6 = 400 MHz
```

**ده إزاي بنحول 24 MHz لـ 800 MHz!** 🎯

---

## 4. الـ Rate Propagation (انتشار السرعة)

### السيناريو:
```
PLL (800 MHz)
    |
Divider (/2)
    |
APB_CLK (400 MHz)
    |
UART_CLK
```

لو **غيّرت** سرعة الـ PLL لـ 1000 MHz، إيه اللي هيحصل؟

### الـ Framework بيعمل كده:

1. **يبدأ من الأب** (PLL)
2. **يحسب السرعة الجديدة** (1000 MHz)
3. **ينزل للأبناء** (Divider)
4. **الـ Divider يحسب سرعته**: 1000 / 2 = 500 MHz
5. **ينزل لـ APB_CLK**: يبقى 500 MHz
6. **UART_CLK** كمان يتأثر!

#### الكود:

```c
unsigned long clk_recalc_rate(struct clk_core *core) {
    unsigned long parent_rate = 0;

    // جيب سرعة الأب
    if (core->parent)
        parent_rate = core->parent->rate;

    // احسب سرعتك بناءً على سرعة الأب
    if (core->ops->recalc_rate)
        return core->ops->recalc_rate(core->hw, parent_rate);

    return parent_rate;  // لو مافيش حاجة، خد سرعة الأب زي ما هي
}
```

---

## 5. الـ clk_hw Abstraction (الطبقة الوسيطة)

### ليه محتاجينه؟

عشان **نفصل** بين:
- الـ **common code** (clk_core)
- الـ **hardware code** (clk_gate, clk_divider...)

```c
struct clk_hw {
    struct clk_core *core;   // pointer للـ core
    struct clk *clk;         // pointer للـ consumer interface
    const struct clk_init_data *init;
};
```

### ازاي بنتنقل بينهم؟

```c
// من hw للـ hardware structure
#define to_clk_gate(_hw) container_of(_hw, struct clk_gate, hw)

// من clk_core للـ hw
struct clk_hw *hw = core->hw;

// من hw للـ clk_core
struct clk_core *core = hw->core;
```

**container_of** دي macro سحرية بتقولك: "أنا عندي عنوان الـ member، طلّعلي عنوان الـ struct كله!"

---

## 6. التسجيل الكامل (Full Registration)

### الخطوات التفصيلية:

#### 1. حضّر الـ init data:
```c
static const char *uart_parents[] = { "pll1", "pll2", "osc24M" };

struct clk_init_data init = {
    .name = "uart_clk",
    .ops = &clk_gate_ops,
    .parent_names = uart_parents,
    .num_parents = 3,
    .flags = CLK_SET_RATE_PARENT,  // لو غيرت سرعتي، غير الأب كمان
};
```

#### 2. املأ الـ hardware structure:
```c
struct clk_gate *gate;
gate = kzalloc(sizeof(*gate), GFP_KERNEL);

gate->reg = ioremap(0x12340000, 4);  // عنوان الـ register
gate->bit_idx = 7;                    // bit رقم 7
gate->hw.init = &init;
```

#### 3. سجّل في الـ framework:
```c
struct clk *clk;
clk = clk_register(NULL, &gate->hw);

if (IS_ERR(clk)) {
    pr_err("Failed to register uart_clk!\n");
    return PTR_ERR(clk);
}
```

#### 4. الـ framework بيعمل ايه جوه؟

```c
// drivers/clk/clk.c
struct clk *clk_register(struct device *dev, struct clk_hw *hw) {
    struct clk_core *core;

    // 1. اعمل clk_core جديد
    core = kzalloc(sizeof(*core), GFP_KERNEL);

    // 2. انسخ البيانات
    core->name = kstrdup(hw->init->name);
    core->ops = hw->init->ops;
    core->hw = hw;
    core->num_parents = hw->init->num_parents;

    // 3. ربط الـ hw بالـ core
    hw->core = core;

    // 4. دوّر على الـ parents
    for (i = 0; i < core->num_parents; i++) {
        core->parents[i] = clk_core_lookup(parent_names[i]);
    }

    // 5. ضيفه للـ clock tree
    clk_core_populate_parent_map(core);

    // 6. احسب السرعة الابتدائية
    if (core->ops->recalc_rate)
        core->rate = core->ops->recalc_rate(core->hw, parent_rate);

    return clk;
}
```

---

## 7. الـ Enable/Disable Reference Counting

### المشكلة:
لو **اتنين drivers** بيستخدموا نفس الـ clock، إيه اللي يحصل؟

```c
// Driver A
clk_enable(usb_clk);  // enable_count = 1

// Driver B
clk_enable(usb_clk);  // enable_count = 2

// Driver A خلص شغله
clk_disable(usb_clk); // enable_count = 1 (لسه شغال!)

// Driver B خلص شغله
clk_disable(usb_clk); // enable_count = 0 (دلوقتي يقفل)
```

### الكود:
```c
int clk_enable(struct clk *clk) {
    unsigned long flags;

    spin_lock_irqsave(&enable_lock, flags);

    if (clk->core->enable_count == 0) {
        // أول مرة نشغله
        clk->core->ops->enable(clk->core->hw);
    }

    clk->core->enable_count++;  // زوّد العداد

    spin_unlock_irqrestore(&enable_lock, flags);

    return 0;
}

void clk_disable(struct clk *clk) {
    unsigned long flags;

    spin_lock_irqsave(&enable_lock, flags);

    if (--clk->core->enable_count == 0) {
        // آخر واحد استخدمه، دلوقتي قفله
        clk->core->ops->disable(clk->core->hw);
    }

    spin_unlock_irqrestore(&enable_lock, flags);
}
```

---

## 8. الـ Rate Change Notification (إشعارات تغيير السرعة)

### ليه محتاجينها؟

بعض الـ drivers عايزة **تعرف** لما السرعة هتتغير!

**مثال:** الـ UART driver لازم يحسب الـ baud rate تاني لو الـ clock اتغير.

```c
struct notifier_block uart_clk_nb = {
    .notifier_call = uart_clk_notifier,
};

// سجّل نفسك عشان تعرف لما الـ clock يتغير
clk_notifier_register(uart_clk, &uart_clk_nb);

// الـ callback
static int uart_clk_notifier(struct notifier_block *nb,
                              unsigned long event, void *data) {
    struct clk_notifier_data *ndata = data;

    switch (event) {
    case PRE_RATE_CHANGE:
        // هيتغير دلوقتي!
        pr_info("Clock changing: %lu -> %lu\n",
                ndata->old_rate, ndata->new_rate);
        // استعد للتغيير
        break;

    case POST_RATE_CHANGE:
        // اتغير فعلاً!
        uart_update_baud_rate(ndata->new_rate);
        break;

    case ABORT_RATE_CHANGE:
        // التغيير اتلغى!
        break;
    }

    return NOTIFY_OK;
}
```

---

## 9. الـ Debugfs Interface (واجهة التصحيح)

### إزاي تشوف الـ clock tree؟

```bash
# اعرض كل الـ clocks
cat /sys/kernel/debug/clk/clk_summary

# Output:
   clock                         enable_cnt  prepare_cnt  rate
------------------------------------------------------------------------
 osc24M                          2           2            24000000
    pll1                         1           1            800000000
       cpu_clk                   1           1            400000000
       ahb_clk                   3           3            200000000
          apb_clk                5           5            100000000
             uart0               1           1            100000000
             uart1               0           0            100000000
             i2c0                1           1            100000000
    pll2                         1           1            600000000
       usb_clk                   1           1            48000000
```

### شوف تفاصيل clock معين:
```bash
cd /sys/kernel/debug/clk/uart0

cat clk_rate
100000000

cat clk_enable_count
1

cat clk_prepare_count
1

cat clk_parent
apb_clk
```

---

## 10. سيناريو واقعي كامل: USB Clock

### المطلوب:
عايزين نعمل USB clock بسرعة **48 MHz** من crystal **24 MHz**.

### الحل:

#### 1. عرّف الـ clocks:
```c
// Crystal الثابت
clk_register_fixed_rate(NULL, "osc24M", NULL, 0, 24000000);

// PLL بيضاعف × 20
// 24 MHz × 20 = 480 MHz
struct clk_pll *pll;
pll->m = 20;  // multiplier
pll->n = 1;   // divider
clk_register(NULL, "pll_usb", &pll->hw);

// Divider بيقسم ÷ 10
// 480 MHz / 10 = 48 MHz
struct clk_divider *div;
div->div = 10;
clk_register(NULL, "usb_pre_clk", &div->hw);

// Gate للتحكم
struct clk_gate *gate;
gate->bit_idx = 23;
clk_register(NULL, "usb_clk", &gate->hw);
```

#### 2. الـ Tree النهائي:
```
osc24M (24 MHz)
    |
pll_usb (480 MHz) = 24 × 20
    |
usb_pre_clk (48 MHz) = 480 / 10
    |
usb_clk (48 MHz) - with gate
```

#### 3. الـ USB driver يستخدمه:
```c
struct clk *clk;

clk = clk_get(dev, "usb_clk");
clk_prepare_enable(clk);  // شغّل الـ USB!

// استخدم الـ USB...

clk_disable_unprepare(clk);  // خلصنا، قفل
```

---

## 11. الـ CLK_SET_RATE_PARENT Flag

### المشكلة:
لو عندك:
```
PLL (800 MHz)
    |
Divider (/2)
    |
UART (400 MHz)
```

وعايز UART بسرعة **115200 baud** اللي محتاج **1.8432 MHz**.

لو قلت:
```c
clk_set_rate(uart_clk, 1843200);
```

الـ **divider** مش هيقدر يطلّع السرعة دي من 800 MHz!

### الحل:

استخدم **CLK_SET_RATE_PARENT**:

```c
struct clk_init_data init = {
    .name = "uart_clk",
    .flags = CLK_SET_RATE_PARENT,  // غيّر الأب لو محتاج!
};
```

دلوقتي لما تقول `clk_set_rate(uart_clk, 1843200)`:
1. الـ divider يحاول يطلّعها من 800 MHz → **مش قادر**
2. يقول للـ PLL: "يا أبويا، غيّر سرعتك!"
3. الـ PLL يغيّر لـ frequency مناسب
4. الـ divider يقسم ويطلّع الـ 1.8432 MHz

---

## 12. الـ Assigned Clocks (التعيين من Device Tree)

في الـ **Device Tree** تقدر تحدد السرعة مباشرة:

```dts
uart0: serial@12340000 {
    compatible = "vendor,uart";
    clocks = <&cru UART0_CLK>;
    clock-names = "uart";

    assigned-clocks = <&cru UART0_CLK>;
    assigned-clock-rates = <1843200>;     // السرعة المطلوبة
    assigned-clock-parents = <&cru PLL2>; // الأب المطلوب
};
```

الـ kernel لما يشوف ده، **تلقائياً** هيعمل:
```c
clk_set_parent(uart0_clk, pll2);
clk_set_rate(uart0_clk, 1843200);
```

---

## الخلاصة الشاملة 🎓

### الـ Common Clock Framework هو:

1. **نظام شجري** - كل clock ليه parent
2. **Reference counting** - عشان ما يقفلش clock حد تاني بيستخدمه
3. **Rate propagation** - لما تغير الأب، الأبناء تحسب نفسها تاني
4. **Multiple types** - fixed, gate, divider, mux, PLL
5. **Two-phase** - prepare (slow) + enable (fast)
6. **Notifications** - عشان الـ drivers تعرف لما حاجة تتغير
7. **Debugfs** - عشان تشوف إيه اللي بيحصل
8. **Device Tree integration** - تقدر تحدد كل حاجة من الـ DTS

**المعادلة السحرية:**
```
Clock Framework = Hardware abstraction + Power management + Rate calculation + Parent management
```

كل ده عشان **توفر طاقة** ✅ و **تدي كل peripheral السرعة اللي محتاجها** ✅!
