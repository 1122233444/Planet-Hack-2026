# 五分钟视频大纲

给 ISECG 发射评审团的视频，用英文讲。结构按第二次工作坊建议的故事线：**开场 → 空间天气 → 威胁 → 利害 → 我们的研究 → 结果和建议 → 结尾**。

**重点（考官要求）：** 第一是防太阳粒子（高能质子），第二是大气阻力。所以开场、"威胁"和"结果"三段都先讲粒子，再讲阻力。结果部分按我们方案的三层来讲：① 预警层、② 辐射安全模式（响应层）、③ 被动屏蔽层。

- 配图全部用 `figures/` 里白底的普通科学图，不用 `figures/video/` 里的深色图。
- 英文台词约 748 词，按每分钟 150 词左右的语速约 5 分钟。录之前先计时练一遍。超时的话，先把 5c 换成短版（见 5c 下面），再删掉 6g 里 "Our calendar predicts…" 那一句。
- 有两处讲局限：5e 讲预测的局限，6g 讲方案的局限。评委看重这个，不要删光。
- 台词里不用破折号，句子尽量短，像说话一样。
- 视频里的每个数字都要和 README 一致。**不要用那份 PDF 报告里的数字**，原因见文末。

> 注：开场不要说 ADEOS-II 是被这次质子风暴打坏的。它在 2003 年 10 月 24 日激波到达后失去电力，原因多半是充放电；而那次质子风暴 10 月 26 日才开始，28–29 日达到最强。

## 一、分段大纲

### 1. 开场（0:00–0:20）

**画面：**
- `data/sdo/hmi_20141215.png`（真实的 SDO 太阳图像）全屏，慢慢放大。
- 先叠字 "Halloween 2003: proton storm 3,000× NOAA's alert level"，再换成 "February 2022: 38 Starlink satellites lost"。

> Halloween 2003. One of the strongest solar proton storms ever measured swept past Earth, three thousand times NOAA's alert level. In 2022, a far weaker storm dragged 38 Starlink satellites out of orbit. ISECG will launch a hundred-billion-dollar satellite system in 2035, whatever the Sun is doing. We are its advisors.

### 2. 空间天气（0:20–0:42）

**画面：** `sdo_daily_strip.png`（7 天里黑子从左往右移动，可以在剪辑软件里平移），然后 `flares_vs_sunspots.png`（黑线是黑子数，柱子是耀斑）。

> Space weather starts at sunspots, knots of magnetic field whose number rises and falls every eleven years. Near the peak they fire flares. The X-rays reach us in eight minutes, and solar particles, mostly protons, arrive minutes to hours later. One to three days after that, clouds of plasma hit Earth's magnetic field.

### 3. 威胁：先讲粒子，再讲阻力（0:42–1:07）

**画面：**
- `protons.png` 左图（每年的质子事件，红色是强事件）。
- 然后 `drag_leo.png` 左图（空气密度：蓝线是低谷，橙线是 2035 年）。

> For a satellite, the particles are the first danger. One proton can flip a bit or lock up a chip, and over the years the dose wears out electronics and solar panels. The second danger is drag. In a maximum year the Sun swells the upper atmosphere. At 550 kilometres the air is fourteen times denser than at minimum, so satellites sink.

### 4. 利害（1:07–1:21）

**画面：** `incidents_timeline.png` 全图（历史事件加上我们对 2035 年的预测）。

> Big storms can strike in any year, but they cluster around the peak and just after it. 2035 is the next peak. The system isn't built yet, so we have seven years to design for it.

### 5. 我们的研究（1:21–2:52）

**5a 手动测量（1:21–1:46）**

**画面：** 你们自己录的测量过程（拍法见第二部分，镜头 1–4），最后 4 秒切到 `manual_steps.png`，证明和程序的结果一致。

> We measured the Sun ourselves. On NASA SDO images, one per day, we found the edges of the disk, left at pixel 64 and right at 1983, giving its centre and radius. Then we read two sunspots at very different latitudes, with the exact time as a Julian Date. A program measured every image, and we checked it by hand, step by step.

**5b 三角函数和正弦拟合（1:46–2:07）**

**画面：** 你们录的表格计算过程，然后 `xy_sine_fit.png`（镜头 5–7）。

> Trigonometry turns pixels into angles. Latitude is arcsin of Y, and longitude is arcsin of X over cos latitude. Plotted against time, each spot's x position traces a sine wave. The fits give 26.1 days at 30 degrees north and 25.4 days at 8 degrees south, so the equator spins faster.

**5c 自转方程（2:07–2:20）**

**画面：** 你们在表格里解两个方程、散点图上出现趋势线公式；然后 `rotation_vs_latitude.png` 左图（21,566 个点组成的云），最后 `rotation_equation.png`（镜头 8–10）。

> Two spots give two equations, enough to solve omega equals A plus B sin squared latitude. Ours give 14.2 minus 1.6. Adding 21,566 groups from 150 years refines it to 14.54 minus 2.84.

短版（不讲两个黑子的推导）：

> With 21,566 sunspot groups from 150 years of records, the rates fall on a straight line: omega equals 14.54 minus 2.84 sin squared latitude, in degrees per day.

**5d 蝴蝶图（2:20–2:34）**

**画面：** `differential_rotation_shear.png` 放 3 秒，然后 `butterfly_own.png`，放大最上面那张。

> This uneven rotation winds up the magnetic field and drives the cycle. Our own butterfly diagram shows cycles starting in 2008.8 and 2020.0, 11.2 years apart, pointing to a peak in 2035 or 2036.

**5e 预测（2:34–2:52）**

**画面：** `forecast_v2_ensemble.png`。讲到 "a range, not a promise" 时，圈出预测分布的宽度。

> Combining fifteen real past cycles into 210 possible futures puts the peak at 2035.4, plus or minus 1.2 years, with a sunspot number around 156. That's a range, not a promise: fifteen cycles is a small sample. Still, the launch falls inside the storm season.

### 6. 结果和建议（2:52–4:44）

结果部分按我们方案的三层来讲：**① 预警 → ② 辐射安全模式 → ③ 被动屏蔽**，然后是阻力、成本和方案的局限。

**6a 2035 年的太阳粒子（2:52–3:02）**

**画面：** `protons.png` 中图（质子事件和黑子数的关系，橙色带是 2035 年）。

> First, the particles. We expect about eleven proton events in 2035, one or two of them strong. A ten-year mission meets about eight strong ones.

**6b ① 预警层（3:02–3:21）**

**画面：** `region_calendar.png`；讲到"GOES alerts"时可以闪一下 `response_playbook.png` 的 Warning/Alert 两行。

> Our particle defence has three layers. One is warning. GOES proton alerts trigger our response automatically. For days of notice, our rotation law tracks the regions behind 85 percent of proton events. For the May 2024 superstorm region, it was right to within a day, five weeks ahead.

注意：不要说"L1 卫星提前发现耀斑和粒子"。L1 只比地球早几秒看到光和高能质子。它的作用是提前 1–3 天看到日冕物质抛射（日冕仪），以及在它撞上地球前 15–60 分钟测到太阳风，这一点在阻力部分可以提一句。

**6c ② 辐射安全模式（3:21–3:34）**

**画面：** `response_playbook.png`（Alert 那一行）。

> Two is a radiation safe mode. The payload switches off and non-essential electronics sleep. The flight computer is our crew. It lives in its vault, with a hot spare and error-correcting memory.

**6d ③ 被动屏蔽（3:34–4:01）**

**画面：** `shielding.png` 中图（地球磁场挡掉多少）→ 右图（剂量随屏蔽厚度下降；星星是我们的保险箱，和 2 g/cm² 纯铝的点一样高，但更靠左，也就是更轻）。

注意："fifty times below the chip limit" 只算了太阳粒子，所以台词里要说 solar-particle dose。辐射带（南大西洋异常区）的剂量我们没有算，见问答第 5 条。

> Three is passive protection. At 53 degrees, Earth's magnetic field alone cuts the dose sixteen-fold. A sealed box wraps the computer, its power and its memory: 3.7 millimetres of aluminium lined with 7.5 millimetres of polyethylene. Its solar-particle dose stays fifty times below the chip limit, and it's a kilogram lighter than solid aluminium. Thicker walls barely help, so layer two handles the protons that still get through.

**6e 其次是阻力（4:01–4:13）**

**画面：** `drag_leo.png` 中图（从多高出发能撑多少天）。

> Second, drag. Coronagraphs warn us one to three days before a storm hits. We deploy at 300 kilometres, not 210, which gives weeks of margin instead of two or three days.

**6f 成本（4:13–4:24）**

**画面：** `layered_protection.png` 全表 → `cost.png`

> With spares in orbit and off-grid ground stations, all this adds twelve kilograms per satellite instead of 234, at six percent of the cost of full hardening.

**6g 我们方案的局限（4:24–4:44）**

**画面：** 白底文字卡，标题 Limitations，四行：radiation belts not modelled / calendar: when, not whether / box untested / costs are estimates；最后一行 Next: radiation-belt model, proton-beam test。

> Our design has limits too. We counted solar particles, not the radiation belts. Our calendar predicts when a region faces us, not whether it erupts. The box is untested, and our costs are estimates. Next, we would model the belts and test the box in a proton beam.

### 7. 结尾（4:44–5:00）

**画面：** 团队出镜。片尾放一张白底字幕，列出数据来源：NASA SDO、NOAA SWPC 和 NCEI（GOES）、WDC-SILSO、GFZ Potsdam、D. Hathaway 的黑子群记录、NRLMSIS 2.1，以及 GitHub 仓库地址。

> Our recommendation: launch in 2035 with these layers built in. Warning, safe mode and shielding against particles first, altitude against drag second. Review the forecast as cycle 26 begins around 2030. 2035 will be stormy, but the system can be ready.

## 二、手动测量和推导方程：怎么拍、怎么算

不要只放一张黑子图片。要你们自己从像素一路算到自转方程 ω = A + B·sin²(纬度)，并把过程录下来：评委看到的是你们在量、在算，台词"我们手动逐步检查"才是真实的。所以鼠标和键盘都要由你们自己操作。

**最少的工作量：** 2 张图 × 2 个黑子 = 4 个黑子位置，加上每张图 4 个边缘。熟练后约 20 分钟，录下来剪成约 1 分钟（1:21–2:20）。

### 0. 准备

- **图片：** 在 GitHub 仓库的 `data/sdo/` 里打开文件，点右上角的下载按钮（Download raw file）。

  | 文件 | 实际拍摄时间（UT） | 用作 |
  |---|---|---|
  | `hmi_20141213.jpg` | 2014-12-12 23:59:40 | 第 1 天 |
  | `hmi_20141218.jpg` | 2014-12-17 23:59:40 | 第 6 天（5 天后） |

  - **注意：** 文件名比实际拍摄日期晚一天。时间以同名 `.json` 里的 `"date"` 为准。
  - 两张图都是 2048×2048 像素，太阳北极朝上。
- **看像素坐标的软件**（都免费）：
  - GIMP（Windows/Mac）：打开菜单"窗口 → 可停靠对话框 → 指针"（Windows → Dockable Dialogs → Pointer）。这个窗口会显示鼠标所在像素的 x、y 和亮度。
  - Fiji/ImageJ：坐标和亮度都显示在主窗口状态栏。
- **算数：** Excel 或 Google 表格。
- **录屏：**
  - 用 OBS Studio（Windows/Mac 都有），或 Windows 的 Win+G、Mac 的 Cmd+Shift+5。
  - 录 1080p。
  - 录之前把表格缩放到 150%，把 GIMP 的指针窗口拖大，让数字在视频里看得清。
- **再准备一部手机**，架在队员身后拍 3 秒肩后镜头。

### 1. 在 GIMP 里量像素（录屏 1）

每张图读 6 个数：4 个边缘，2 个黑子。读之前放大到 800%（视图 → 缩放 → 8:1），鼠标停稳再读指针窗口里的 x、y。

- **左、右边缘：** 沿着中间的横线（y ≈ 1024）从外面的黑往里移。亮度从十几一下跳到四五十的那个像素就是边缘。
- **上、下边缘：** 同样的方法，沿竖线（x ≈ 1024）找。
- **黑子：** 把鼠标放在黑子中间最黑那一小块（本影）的中心。
- **怎么找到 A 和 E：** 第 1 天的位置见 `figures/manual_steps.png` 里的红圈。到第 6 天：
  - A 转到了圆心正上方偏右，大约在上边缘和圆心的中间。
  - E 的高度几乎不变，转到了圆心和右边缘的中间。

应该读到下面这些数。差 1–3 个像素是正常的；**如果差别正好是这个大小，就在视频里说出来**，评委会觉得更真实。

| 读数 | `hmi_20141213.jpg`（第 1 天） | `hmi_20141218.jpg`（第 6 天） |
|---|---|---|
| 左边缘 x | 64 | 65 |
| 右边缘 x | 1983 | 1983 |
| 上边缘 y | 65 | 65 |
| 下边缘 y | 1984 | 1984 |
| 黑子 A（北纬约 30°） | (302, 553) | (1082, 528) |
| 黑子 E（南纬约 7°） | (455, 1147) | (1486, 1143) |

### 2. 在表格里把像素变成角度（录屏 2）

**表格布局：**
- 第 1 行写标题。
- 第 2–5 行，每一行是"一个黑子在一张图上"，依次是：A 第 1 天、A 第 6 天、E 第 1 天、E 第 6 天。
- 公式写在第 2 行，然后往下拖到第 5 行。

| 列 | 内容 | 第 2 行的公式 | A 第 1 天应得 |
|---|---|---|---|
| A | 黑子 | 手填 A 或 E | A |
| B、C、D | 年、月、日 | 手填（第 6 天的日填 17） | 2014、12、12 |
| E | 时间（UT，小时） | `=23+59/60+40/3600` | 23.99444 |
| F | 儒略日 JD | `=367*B2-INT(7*(B2+INT((C2+9)/12))/4)+INT(275*C2/9)+D2+1721013.5+E2/24` | 2457004.49977 |
| G、H、I、J | 左、右、上、下边缘 | 手填 | 64、1983、65、1984 |
| K | 圆心 x | `=(G2+H2)/2` | 1023.5 |
| L | 圆心 y | `=(I2+J2)/2` | 1024.5 |
| M | 半径 | `=((H2-G2)+(J2-I2))/4` | 959.5 |
| N、O | 黑子 x、y | 手填 | 302、553 |
| P | X（向右为正） | `=(N2-K2)/M2` | −0.7520 |
| Q | Y（向上为正） | `=-(O2-L2)/M2` | 0.4914 |
| R | 纬度 | `=DEGREES(ASIN(Q2))` | 29.43° |
| S | 经度（离中央经线） | `=DEGREES(ASIN(P2/COS(RADIANS(R2))))` | −59.70° |

- Q 列有负号，因为图片的 y 往下增大，而太阳的北在上面。
- 儒略日也可以这样验算：Excel 里日期时间格的数值加上 2415018.5。

四行都应该得到：

| 行 | 黑子 | JD | 圆心、半径 | X | Y | 纬度 | 经度 |
|---|---|---|---|---|---|---|---|
| 2 | A 第 1 天 | 2457004.49977 | 1023.5、1024.5、959.5 | −0.7520 | 0.4914 | 29.43° | −59.70° |
| 3 | A 第 6 天 | 2457009.49977 | 1024.0、1024.5、959.25 | 0.0605 | 0.5176 | 31.17° | 4.05° |
| 4 | E 第 1 天 | 2457004.49977 | 1023.5、1024.5、959.5 | −0.5925 | −0.1277 | −7.34° | −36.68° |
| 5 | E 第 6 天 | 2457009.49977 | 1024.0、1024.5、959.25 | 0.4816 | −0.1235 | −7.10° | 29.04° |

### 3. 每个黑子转多快（接着录屏 2）

第 8 行写标题。第 9 行是黑子 A，第 10 行是黑子 E；E 的公式把行号 2、3 换成 4、5。

| 列 | 内容 | A 的公式（第 9 行） | A 应得 | E 应得 |
|---|---|---|---|---|
| B | 从地球看的转速（°/天） | `=(S3-S2)/(F3-F2)` | 12.750 | 13.144 |
| C | 真实转速 ω（°/天） | `=B9+1.017` | 13.767 | 14.161 |
| D | 真实周期（天） | `=360/C9` | 26.15 | 25.42 |
| E | 平均纬度 | `=AVERAGE(R2:R3)` | 30.30° | −7.22° |
| F | sin²(纬度) | `=SIN(RADIANS(E9))^2` | 0.2546 | 0.0158 |

**为什么加 1.017：**
- 地球也在绕太阳转，方向和太阳自转相同，所以从地球上看，黑子显得转慢了。
- 12 月地球离太阳近（1 月初过近日点），每天公转约 1.017°（全年平均 0.986°）。
- 所以：真实转速 = 看到的转速 + 地球每天转过的角度。

到这一步已经能看出：赤道附近的 E 转一圈 25.4 天，北纬 30° 的 A 要 26.1 天。赤道转得快。

### 4. 推导方程（录屏 3，这一段的核心）

推导分四步。录的时候边做边讲，后期配台词也行。

1. **测量结果：** 北纬 30° 的 A 每天转 13.77°，南纬 7° 的 E 每天转 14.16°。转速随纬度变，所以要找一个"转速 = 纬度的函数"。
2. **假设方程的形式：**
   - 太阳南北对称：南纬 7° 和北纬 7° 转得一样快，所以方程里只能出现纬度的偶次量。
   - 最简单的就是 sin²(纬度)，所以设 **ω = A + B·sin²(纬度)**。
   - 天文学家还会加一项 C·sin⁴，它只在 40° 以上才有影响，而那里几乎没有黑子。
3. **两个未知数要两个方程，也就是两个不同纬度的黑子。** 这正是题目要求跟踪两个不同纬度黑子的原因。
   - 黑子 A：13.767 = A + B × 0.2546
   - 黑子 E：14.161 = A + B × 0.0158
   - 两式相减：13.767 − 14.161 = B × (0.2546 − 0.0158)，所以 B = −0.394 ÷ 0.2388 = **−1.65**
   - 代回 E 的式子：A = 14.161 − (−1.65) × 0.0158 = **14.19**
   - 得到 **ω = 14.19 − 1.65·sin²(纬度)**（度/天）。赤道转一圈 360 ÷ 14.19 = 25.4 天。
4. **用更多数据检验形式对不对：** 如果形式对，以 sin²(纬度) 为横轴画转速，点应该排成一条直线。150 年 21,566 个黑子群确实排成直线，得到 ω = 14.54 − 2.84·sin²(纬度)（`rotation_equation.png`）。

**表格公式：**

| 格子 | 公式 | 应得 |
|---|---|---|
| B12（B） | `=(C9-C10)/(F9-F10)` | −1.647 |
| B13（A） | `=C10-B12*F10` | 14.187 |
| B14（赤道周期） | `=360/B13` | 25.38 天 |
| 验算 | `=SLOPE(C9:C10,F9:F10)` 和 `=INTERCEPT(C9:C10,F9:F10)` | 同样的 −1.647 和 14.187 |

**画方程图（视频里最好看的画面）：**
1. 在 H9 写 `=F9`，I9 写 `=C9`，再往下拖到第 10 行。这样横轴 sin²(纬度) 在左边一列，纵轴 ω 在右边一列。
2. 选中 H9:I10，插入散点图。
3. 加趋势线：
   - Excel：右键点一个点 → 添加趋势线 → 线性 → 勾选"显示公式"。
   - Google 表格：图表编辑器 → 自定义 → 系列 → 勾选趋势线 → 标签选"使用公式"。
4. 图上会出现 **y = −1.6468x + 14.187**。这就是你们的方程：x 是 sin²(纬度)，y 是 ω。

你们自己量的像素差几个，B 落在 −1.4 到 −1.9 之间都正常。

### 5. 选做：7 张图都量

时间够的话，把 7 张图都量了：A 在 `hmi_20141213` 到 `hmi_20141218` 这 6 张上，E 在全部 7 张上。
- 每个黑子的转速改用 `=SLOPE(经度那几格, JD那几格)`，不再只用头尾两天。
- 应得：A 12.767 °/天 → 真实 13.784，周期 26.12 天；E 13.155 → 14.172，周期 25.40 天。
- 方程是 ω = 14.20 − 1.62·sin²(纬度)，和只用 2 张图几乎一样，说明结果稳定。
- 每一天的读数可以对照 `data/rotation/manual_walkthrough.csv`。
- 再以 JD 为横轴画 x 的散点图，能看出点排在一条正弦曲线上，和 `xy_sine_fit.png` 一样。

### 6. 我们做了哪些假设（要求 3，评委会问）

1. **太阳是球体，图片北在上，我们从很远处看。** 忽略了太阳自转轴朝地球的倾斜 B0（那一周是 −0.6° 到 −1.3°）。所以表格算出 E 在 −7.2°，程序加上 B0 修正后是 −8.0°；A 是 30.3°，修正后 29.5°。
2. **黑子跟着太阳表面一起转，自己不动。** 实际上 A 五天里往北漂了约 1.7°（29.4° → 31.2°），这是误差来源之一。
3. **这一周里地球公转速度不变**，取 1.017°/天。
4. **南北对称**，ω = A + B·sin²(纬度) 在 40° 以下够用。
5. **只用离中央经线 60° 以内的位置。** 太靠近边缘时，1 个像素的误差会变成很大的角度误差。

### 7. 为什么两个黑子的结果和 150 年的不一样

- **两个黑子：** ω = 14.19 − 1.65·sin²(纬度)；**150 年：** 14.54 − 2.84·sin²(纬度)。
- 北纬 30° 两者几乎一样（13.77 对 13.83 °/天），差别主要在赤道附近。
- **原因：** 单个黑子群本来就会比同纬度的平均转得快一点或慢一点。150 年的数据里，这个散布约 ±0.5 °/天。E 比同纬度的 150 年平均慢约 0.3 °/天，在正常范围内。
- B 是两个转速之差除以 0.24，所以一个黑子偏 0.5 °/天，B 就会偏约 2。
- **结论：** 两个黑子足以推导出方程的形式、证明赤道转得快；要得到准确的系数，需要大量黑子。这就是我们接着用 21,566 个黑子群的原因。在视频里直接这样说，评委会认为你们理解了误差。

### 8. 剪辑（1:21–2:20，接在 5a、5b、5c 三段里）

录的时候可以录 20–30 分钟，剪辑时加速 4–8 倍。

| 镜头 | 段落 | 时长 | 内容 |
|---|---|---|---|
| 1 | 5a | 3 秒 | 手机拍的肩后镜头：队员握着鼠标，屏幕上是太阳图像（证明是你们在做） |
| 2 | 5a | 10 秒，加速 | GIMP：放大到左边缘，指针窗口停在 x = 64；再移到黑子 A，(302, 553) |
| 3 | 5a | 8 秒，加速 | 切到第 6 天的图：A 已经转到 (1082, 528)，黑子在动 |
| 4 | 5a | 4 秒 | `manual_steps.png`：程序给出同样的数 |
| 5 | 5b | 10 秒，加速 | 表格：一行行填进去，纬度、经度两列出现 |
| 6 | 5b | 4 秒 | 放大周期那两格：26.15 天和 25.42 天 |
| 7 | 5b | 6 秒 | `xy_sine_fit.png` |
| 8 | 5c | 7 秒，加速 | 表格：两式相减求 B，代回求 A；散点图加上趋势线，放大 y = −1.6468x + 14.187 |
| 9 | 5c | 3 秒 | `rotation_vs_latitude.png` 左图 |
| 10 | 5c | 3 秒 | `rotation_equation.png`：金色星星就是 A 和 E |

**可选：** 把图打印在 A4 纸上，用尺子量（以毫米为单位）拍几秒作为插入画面。这样很有"动手"感，但精度不如像素，所以不要用它的数。

## 三、怎么让科学图在视频里看得清

- 三联图（`shielding.png`、`drag_leo.png`、`geomagnetic_storms.png`、`protons.png`、`rotation_vs_latitude.png`、`flares_relation.png`）宽约 2,400–2,550 像素。只放其中一张图时，在剪辑软件里放大到那一块，每块约 800 像素宽，放到 1080p 里依然清楚。
- 不要给图加特效。需要强调某个点时，用一个简单的圆圈或箭头。
- 每张图出现时，台词说的数字要能在图上找到。

## 四、评委可能会问的问题（录之前准备好答案）

工作坊说过："有最好的数据，讲不清、守不住也没用。"

1. **"宇航员避难舱要 10 g/cm²，为什么电脑的保险箱这么薄？"**
   我们按 GOES 实测数据算过：我们的保险箱（3.7 mm 铝加 7.5 mm 聚乙烯，1.71 g/cm²）挡住的剂量和 2 g/cm² 纯铝一样。53° 轨道上 10 年的太阳质子剂量是 0.2 krad，磁层外是 1.8 krad，都远低于商用芯片约 10 krad 的上限。做到 10 g/cm²，箱壁重约 6 倍（36 kg 对 6.2 kg），剂量本来就已经够低了；而能引发单粒子翻转的高能质子，10 g/cm² 时也还有 11–15% 穿过。所以多出的质量花在冗余和安全模式上更划算。电脑和人的区别是：人可以风暴时才躲进去，电脑一直待在保险箱里。
2. **"为什么外面用铝、里面衬聚乙烯？"**
   聚乙烯含氢多，按同样重量算，减慢质子的效果比铝好，所以同样的剂量能轻约 1 kg。但聚乙烯是绝缘体，又不导热：单用它要 14.6 mm 厚，会积累电荷、把电脑的热捂住。所以外层用铝做结构、导热、接地，电脑装在铝上散热，聚乙烯只做内衬，放在金属里面。
3. **"L1 卫星能提前多久发现太阳粒子？"**
   几乎不能提前。L1 离太阳只比地球近 150 万 km，光只早约 5 秒到，高能质子也只早几秒到一两分钟。粒子的预警时间来自"耀斑的光 8 分钟到、质子要几十分钟到几小时后才到"，以及我们提前几天到几周的活动区日历。L1 的价值在日冕物质抛射：日冕仪提前 1–3 天看到它出发，太阳风监测在它撞上地球前 15–60 分钟测到。要更早看到粒子的源头，要靠欧空局约 2031 年发射到 L5 的 Vigil，它能早约 4.5 天看到转过来的活动区。
4. **"你们的剂量算得对吗？"**
   用的是 GOES 卫星实测的质子数据，每次事件的最高通量和 NOAA 列表对得上（例如 42,200 对 40,000）。质子在铝里的射程和 NIST 的标准值只差 0.1%。用的是标准的直线近似；忽略次级粒子在 2 g/cm² 时影响很小。
5. **"辐射带和南大西洋异常区算了吗？"**
   没有，这是局限。所以台词里说的是 solar-particle dose 低 50 倍。近地轨道上那里的质子会带来持续的剂量。保险箱同样能挡掉一部分，下一步可以用 AE9/AP9 辐射带模型（美国空军研究实验室牵头开发）来算。
6. **"你们真的自己测了吗？"**
   测了。两个黑子的位置是我们在图上手动读的，再用表格一步步算出方程，录像可以证明（如实说你们量了几张图）。另外用程序测了 9 个黑子；150 年的方程用的是 D. Hathaway 整理的天文台黑子群记录。
7. **"2035.4 ± 1.2 年准吗？"**
   这是 210 种历史组合的分布，不是保证。蝴蝶图法得到 2036.4，13 个周期平均是 2034.8。三种方法都落在 2035 年前后一年里，而发射正好在风暴季里面。2029–2031 年看到第 26 周期的高纬度黑子后，可以把预测收紧。
8. **"为什么不全面加固？"**
   每颗卫星要多 234 kg，每年的成本约是我们方案的 16 倍。而且全面加固也救不了 2022 年那批 Starlink：它们是被大气阻力拖下来的，不是被辐射打坏的。
9. **"你们两个黑子得到的 B 是 −1.6，150 年的是 −2.84，为什么差这么多？"**
   单个黑子群本来就会比同纬度的平均转得快一点或慢一点，150 年的数据里散布约 ±0.5 °/天；E 比平均慢约 0.3 °/天，在正常范围内。B 是两个转速之差除以 0.24，一个黑子偏 0.5 °/天，B 就偏约 2。所以两个黑子能推出方程的形式、证明赤道转得快，准确的系数要靠 21,566 个黑子群。北纬 30° 两个方程几乎一样（13.77 对 13.83 °/天）。

## 五、为什么不要用那份 PDF 报告里的数字

那份报告和仓库对不上，评委一查 GitHub 就会发现：
- 它说用了"2010–2026 年 16 年的 SDO 图像，检测到 253,104 个黑子群"。仓库里没有这个分析。实际上 150 年的自转方程来自 D. Hathaway 的黑子群记录，SDO 图像只有 2014 年 12 月的 7 天。
- 它的加固方案（8 g/cm² 保险箱、剂量从 88.8% 降到 1.0%、20,000 颗卫星、我们的方案 22 亿美元占 2.2%、全面加固 720 亿美元占 72%）来自 `scripts/hardening.py`，仓库里没有这个文件，没法复现，而且和 `cost.py` 的结果不一样。
- 我们用 GOES 实测数据算的结果（`shielding.py`）表明，2 g/cm² 已经够用；做到 8 g/cm² 是把质量花在了回报很小的地方。

视频一律用本文和 README 里的数字。
