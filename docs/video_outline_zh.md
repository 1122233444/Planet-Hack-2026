# 五分钟视频大纲

给 ISECG 发射评审团的视频，用英文讲。结构按第二次工作坊建议的故事线：**开场 → 空间天气 → 威胁 → 利害 → 我们的研究 → 结果和建议 → 结尾**。

**重点（考官要求）：** 第一是防太阳粒子（高能质子），第二是大气阻力。所以开场、"威胁"和"结果"三段都先讲粒子，再讲阻力。

- 配图全部用 `figures/` 里白底的普通科学图，不用 `figures/video/` 里的深色图。
- 英文台词约 740 词，按每分钟 150 词左右的语速约 5 分钟，要讲得稍快一点。录之前先计时练一遍，超时就删减第 5 段。
- 视频里的每个数字都要和 README 一致。**不要用那份 PDF 报告里的数字**，原因见文末。

## 一、分段大纲

### 1. 开场（0:00–0:20）

**画面：**
- `data/sdo/hmi_20141215.png`（真实的 SDO 太阳图像）全屏，慢慢放大。
- 先叠字 "Halloween 2003: proton storm 3,000× NOAA's alert level"，再换成 "February 2022: 38 Starlink satellites lost"。

> Halloween 2003. One of the strongest solar proton storms ever measured — about three thousand times NOAA's alert level — and Japan lost its ADEOS-II satellite. In 2022, a far weaker storm dragged 38 new Starlink satellites out of orbit. ISECG will launch a 100-billion-dollar satellite system in 2035, whatever the Sun is doing. We are its advisors.

### 2. 空间天气（0:20–0:45）

**画面：** `sdo_daily_strip.png`（7 天里黑子从左往右移动，可以在剪辑软件里平移），然后 `flares_vs_sunspots.png`（黑线是黑子数，柱子是耀斑）。

> Space weather starts at sunspots: knots of magnetic field whose number rises and falls every eleven years. Near the peak they fire flares — X-rays that reach us in eight minutes — and launch solar energetic particles: protons that arrive minutes to hours later. Then clouds of plasma hit Earth's magnetic field a day or two after that.

### 3. 威胁：先讲粒子，再讲阻力（0:45–1:15）

**画面：**
- `protons.png` 左图（每年的质子事件，红色是强事件）。
- 然后 `drag_leo.png` 左图（空气密度：蓝线是低谷，橙线是 2035 年）。

> For a satellite, the particles are the first danger. A single proton can flip a bit in a computer or lock up a chip, and over the years the dose wears out electronics and solar panels. The second danger is drag: storms heat the upper atmosphere — at 550 kilometres, the air in a maximum year is fourteen times denser than at minimum — so satellites sink.

### 4. 利害（1:15–1:30）

**画面：** `incidents_timeline.png` 全图（历史事件加上我们对 2035 年的预测）。

> Big storms can strike in any year, but they are far more common near the peak — and 2035 sits at the next one. The system isn't built yet. We have seven years to design for it.

### 5. 我们的研究（1:30–3:00）

**5a 手动测量（1:30–1:55）**

**画面：** 你们自己录的测量过程（拍法见第二部分），最后 2 秒切到 `manual_steps.png`，证明和程序的结果一致。

> We measured the Sun ourselves. On NASA SDO images, one per day, we found the edges of the disk — left at pixel 64, right at 1983 — and so its centre and radius. Then we read the pixel position of two sunspots at very different latitudes, with the exact time as a Julian Date. A program measured every image; we checked it by hand, step by step.

**5b 三角函数和正弦拟合（1:55–2:15）**

**画面：** 你们录的表格计算过程，然后 `xy_sine_fit.png`。

> Trigonometry turns pixels into angles: latitude is arcsin of Y; longitude is arcsin of X over cos latitude. Plotted against time, each spot's x position traces a sine wave. The fits give 26.1 days at 30° north and 25.4 days at 8° south: the equator spins faster.

**5c 自转方程（2:15–2:28）**

**画面：** `rotation_vs_latitude.png` 左图（21,566 个点组成的云），然后 `rotation_equation.png`。

> With 21,566 sunspot groups from 150 years of observatory records, the rates fall on a straight line: omega equals 14.54 minus 2.84 sin² latitude, degrees per day.

**5d 蝴蝶图（2:28–2:45）**

**画面：** `differential_rotation_shear.png` 放 3 秒，然后 `butterfly_own.png`，放大最上面那张。

> This uneven rotation winds up the magnetic field — the engine of the cycle. Our own butterfly diagram shows new cycles starting in 2008.8 and 2020.0: an 11.2-year cycle, pointing to a peak in 2035 to 2036.

**5e 预测（2:45–3:00）**

**画面：** `forecast_v2_ensemble.png`

> Combining fifteen real past cycles into 210 possible futures puts the peak at 2035.4, plus or minus 1.2 years, with a sunspot number around 156. The launch is inside the storm season.

### 6. 结果和建议（3:00–4:40）

**6a 2035 年的太阳粒子（3:00–3:10）**

**画面：** `protons.png` 中图（质子事件和黑子数的关系，橙色带是 2035 年）。

> First, the particles. Forty years of NOAA records give about eleven proton events in 2035, one or two of them strong — and a ten-year mission will meet about eight strong ones.

**6b 怎么挡（3:10–3:35）**

**画面：** `shielding.png` 的三张图依次放大：左（GOES 测到的最大几次事件）→ 中（地球磁场挡掉多少）→ 右（剂量随铝厚度下降，绿线是我们的保险箱）。

> We took GOES measurements of the worst proton storms on record and calculated the dose behind shielding. The Earth's magnetic field is the first shield: at 53 degrees, an unshielded part gets one-sixteenth of the dose in open space. A vault of just two grams per square centimetre — seven millimetres of aluminium — cuts the ten-year dose to 0.2 krad, fifty times below what commercial chips survive. Thicker walls barely help.

**6c 挡不住的部分（3:35–3:50）**

**画面：** 还是 `shielding.png` 右图，然后 `layered_protection.png` 放大第 3 行。

> But about half of the protons that flip bits still get through the vault. So the vault holds redundant computers with error-correcting memory, and the satellite goes into safe mode when a proton alert arrives — minutes to hours after the flare.

**6d 提前看到（3:50–4:02）**

**画面：** `region_calendar.png`

> Eighty-five percent of proton events come from regions facing Earth or to its west. Our rotation law predicts when a region gets there: for the region behind the May 2024 superstorm, it was right to within a day, five weeks ahead.

**6e 其次是阻力（4:02–4:15）**

**画面：** `drag_leo.png` 中图（从多高出发能撑多少天）。

> Second, drag: deploy at 300 kilometres, not 210 — three weeks of margin in a storm instead of two days — and operate near 550.

**6f 整体方案和成本（4:15–4:40）**

**画面：** `layered_protection.png` 全表 → `response_playbook.png` → `cost.png`

> With spares in orbit, ground stations that can run off-grid and a response playbook for every NOAA alert level, that is our layered defence. The cost: thirteen kilograms per satellite instead of 234 for full hardening — about 80 million dollars a year, six percent of the alternative.

### 7. 结尾（4:40–5:00）

**画面：** 团队出镜。片尾放一张白底字幕，列出数据来源：NASA SDO、NOAA SWPC 和 NCEI（GOES）、WDC-SILSO、GFZ Potsdam、D. Hathaway 的黑子群记录、NRLMSIS 2.1，以及 GitHub 仓库地址。

> Our recommendation: launch in 2035 with these layers built in — the magnetic field, a small vault and a safe mode against particles first, altitude against drag second — and review the forecast as cycle 26 begins around 2030. 2035 will be stormy. The system can be ready.

## 二、手动测量怎么拍

不要只放一张黑子图片。要真的量一遍，把过程录下来：评委看到的是你们在量，台词"我们手动逐步检查"才是真实的。

### 准备

- **图片：** 用仓库里的 `data/sdo/hmi_20141213.jpg`（2048×2048 像素），我们的手动测量表用的就是这张。
  - **注意：** 文件名写的是 13 日，但这张图实际拍摄于 **2014-12-12 23:59:40 UT**。时间写在同名的 `hmi_20141213.json` 里（`"date"` 那一项），要用这个时间。
- **看像素坐标的软件**（都免费）：
  - GIMP（Windows/Mac）：鼠标移到哪里，窗口左下角就显示坐标；"指针"窗口还能显示亮度。
  - Fiji/ImageJ：坐标和亮度都显示在主窗口状态栏。
  - Windows 自带的画图：左下角也显示坐标。
- **录屏：**
  - Windows：Win+G，或者 OBS Studio。
  - Mac：Cmd+Shift+5。
  - 录 1080p。把软件界面字体调大，或者在剪辑时放大坐标那一块，让评委看得清数字。
- **算数：** Excel 或 Google 表格。
- **再准备一部手机**，架在队员身后拍肩膀和屏幕。

### 量什么、应该得到什么

1. **左边缘：** 放大到 800% 左右，鼠标沿着中间那条横线（y ≈ 1024）从黑往亮移动。亮度从十几一下跳到四五十的那个像素就是边缘，应该在 **x = 64**。
2. **右、上、下边缘：** 同样的方法，应该是右 **1983**、上 **65**、下 **1984**。上下边缘沿竖线 x ≈ 1024 找。
3. **圆心和半径：**
   - 圆心 = ((64 + 1983)/2, (65 + 1984)/2) = **(1023.5, 1024.5)**
   - 半径 = (1983 − 64)/2 = **959.5**
4. **黑子 A：** 在左上方，放大，把鼠标放在中间最黑的那一小块（本影）的中心，应该在 **(302, 553)**。
5. **黑子 E：** 在左下方，应该在 **(455, 1147)**。
6. **其他天：** 至少再量两三张，最好 7 张都量。仓库里的 `data/rotation/manual_walkthrough.csv` 有我们每一天的数，可以对照。

你们量出来的数和我们差 1–3 个像素是正常的，只会让周期差 0.1 天左右。**如果差别正好是这个大小，就在视频里说出来**，评委会觉得更真实。

### 表格里的公式（Excel / Google 表格）

| 算什么 | 公式 | 黑子 A 第一张图的结果 |
|---|---|---|
| 儒略日（UT 写成小时，23:59:40 = 23.9944） | `=367*Y-INT(7*(Y+INT((M+9)/12))/4)+INT(275*M/9)+D+1721013.5+UT/24` | 2457004.49977 |
| X | `=(x-1023.5)/959.5` | −0.752 |
| Y | `=-(y-1024.5)/959.5` | +0.491 |
| 纬度 | `=DEGREES(ASIN(Y))` | +29.4° |
| 经度（离中央经线） | `=DEGREES(ASIN(X/COS(RADIANS(纬度))))` | −59.7°；5 天后的那张图是 +4.1° |
| 从地球看的转速 | `=(最后经度-最初经度)/(最后JD-最初JD)` | 63.8° ÷ 5 天 = 12.75 °/天 |
| 真实周期（加上地球 12 月每天 1.017° 的公转） | `=360/(转速+1.017)` | **26.1 天** |

再把 x 对 JD 画一张散点图，能看出点排在一条正弦曲线上。

### 剪辑成 25 秒（放在 1:30–1:55）

录的时候可以录 10 分钟，剪辑时加速 4–8 倍：

| 镜头 | 时长 | 内容 |
|---|---|---|
| 1 | 3 秒 | 手机拍的肩后镜头：队员握着鼠标，屏幕上是太阳图像（证明是你们在做） |
| 2 | 8 秒，加速 | 录屏：放大到左边缘，坐标停在 x = 64；再移到黑子 A，坐标 (302, 553) |
| 3 | 8 秒，加速 | 录屏：表格里一格格填进去，最后出现 26.1 天 |
| 4 | 2 秒 | 切到 `manual_steps.png`：程序给出同样的数 |
| 5 | 4 秒 | 散点图里的正弦形状，接到下一段的 `xy_sine_fit.png` |

**可选：** 把图打印在 A4 纸上，用尺子量（以毫米为单位）拍几秒作为插入画面。这样很有"动手"感，但精度不如像素，所以不要用它的数。

## 三、怎么让科学图在视频里看得清

- 三联图（`shielding.png`、`drag_leo.png`、`geomagnetic_storms.png`、`protons.png`、`rotation_vs_latitude.png`、`flares_relation.png`）宽约 2,400–2,550 像素。只放其中一张图时，在剪辑软件里放大到那一块，每块约 800 像素宽，放到 1080p 里依然清楚。
- 不要给图加特效。需要强调某个点时，用一个简单的圆圈或箭头。
- 每张图出现时，台词说的数字要能在图上找到。

## 四、评委可能会问的问题（录之前准备好答案）

工作坊说过："有最好的数据，讲不清、守不住也没用。"

1. **"为什么保险箱只要 2 g/cm²？再厚一点不是更安全吗？"**
   2 g/cm² 已经把 10 年的太阳质子剂量降到磁层外 1.8 krad（降到约 1/28）、53° 轨道 0.2 krad（约 1/16），远低于商用芯片约 10 krad 的上限。加到 5 g/cm²，保险箱重 2.5 倍，剂量只多降 4 倍。而能引发单粒子翻转的高能质子，2 g/cm² 时仍有约一半穿过，10 g/cm² 时也还有 11–15%，那要靠冗余和安全模式。
2. **"你们的剂量算得对吗？"**
   用的是 GOES 卫星实测的质子数据，每次事件的最高通量和 NOAA 列表对得上（例如 42,200 对 40,000）。质子在铝里的射程和 NIST 的标准值只差 0.1%。用的是标准的直线近似；忽略次级粒子在 2 g/cm² 时影响很小。
3. **"辐射带和南大西洋异常区算了吗？"**
   没有，这是局限。近地轨道上那里的质子会带来持续的剂量。保险箱同样能挡掉一部分，下一步可以用 NASA 的辐射带模型来算。
4. **"你们真的自己测了吗？"**
   测了两个黑子、7 张图，手动逐步完成，录像可以证明。另外用程序测了 9 个黑子；150 年的方程用的是 D. Hathaway 整理的天文台黑子群记录。
5. **"2035.4 ± 1.2 年准吗？"**
   这是 210 种历史组合的分布，不是保证。蝴蝶图法得到 2036.4，13 个周期平均是 2034.8。三种方法都落在 2035 年前后一年里，而发射正好在风暴季里面。2029–2031 年看到第 26 周期的高纬度黑子后，可以把预测收紧。
6. **"为什么不全面加固？"**
   每颗卫星要多 234 kg，每年的成本约是我们方案的 16 倍。而且全面加固也救不了 2022 年那批 Starlink：它们是被大气阻力拖下来的，不是被辐射打坏的。

## 五、为什么不要用那份 PDF 报告里的数字

那份报告和仓库对不上，评委一查 GitHub 就会发现：
- 它说用了"2010–2026 年 16 年的 SDO 图像，检测到 253,104 个黑子群"。仓库里没有这个分析。实际上 150 年的自转方程来自 D. Hathaway 的黑子群记录，SDO 图像只有 2014 年 12 月的 7 天。
- 它的加固方案（8 g/cm² 保险箱、剂量从 88.8% 降到 1.0%、20,000 颗卫星、我们的方案 22 亿美元占 2.2%、全面加固 720 亿美元占 72%）来自 `scripts/hardening.py`，仓库里没有这个文件，没法复现，而且和 `cost.py` 的结果不一样。
- 我们用 GOES 实测数据算的结果（`shielding.py`）表明，2 g/cm² 已经够用；做到 8 g/cm² 是把质量花在了回报很小的地方。

视频一律用本文和 README 里的数字。
