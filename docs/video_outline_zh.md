# 五分钟视频大纲

给 ISECG 发射评审团的视频，用英文讲。结构按第二次工作坊建议的故事线：**开场 → 空间天气 → 威胁 → 利害 → 我们的研究 → 结果和建议 → 结尾**。

- 配图全部用 `figures/` 里白底的普通科学图，不用 `figures/video/` 里的深色图。
- 英文台词约 700 词，按每分钟 140 词左右的语速约 5 分钟。录之前先计时练一遍，超时就删减第 6 段。
- 视频里的每个数字都要和 README 一致。**不要用那份 PDF 报告里的数字**，原因见文末。

## 一、分段大纲

### 1. 开场（0:00–0:20）

**画面：**
- `data/sdo/hmi_20141215.png`（真实的 SDO 太阳图像），全屏，慢慢放大。
- 叠一行白字："February 2022: 38 Starlink satellites lost to a minor solar storm"。

> February 2022. A minor solar storm swelled Earth's upper atmosphere, and 38 brand-new Starlink satellites fell back and burned up. ISECG will launch a 100-billion-dollar satellite system in 2035, whatever the Sun is doing. We are its advisors. Our job: say what 2035 will bring, and how to survive it.

### 2. 空间天气（0:20–0:50）

**画面：**
- `sdo_daily_strip.png`：7 天的太阳图像排成一排，黑子一天天从左往右移动。可以在剪辑软件里从左到右平移。
- 然后 `flares_vs_sunspots.png`：黑线是黑子数，柱子是耀斑，能看出 11 年的起伏。

> Space weather starts at sunspots: knots of magnetic field on the Sun. Their number rises and falls every eleven years. Around the peak they fire flares — X-rays that reach us in eight minutes and black out radio; energetic protons that arrive within hours; and clouds of plasma, CMEs, that hit Earth's magnetic field one to three days later and cause geomagnetic storms.

### 3. 威胁（0:50–1:20）

**画面：**
- `protons.png` 左图（每年的质子事件）。
- `drag_leo.png` 左图（空气密度随高度变化，蓝线是低谷，橙线是 2035 年）。
- 最后 `incidents_timeline.png`，放大 1989 年魁北克那个标签。

> Each one hurts satellites differently. Protons flip bits and wear out chips. Storms charge satellite surfaces until they spark, and they heat the upper atmosphere: at 550 kilometres the air in a maximum year is fourteen times denser than at minimum, so satellites sink. On the ground, storms push currents into power grids — in 1989 they blacked out Québec.

### 4. 利害（1:20–1:35）

**画面：** `incidents_timeline.png` 全图：历史事件加上我们对 2035 年的预测。

> Big flares and storms can strike in any year, but they are far more common near the peak — and 2035 sits at the next one. The system isn't built yet. We have seven years to design for it.

### 5. 我们的研究（1:35–3:15）

**5a 手动测量（1:35–2:00）**

**画面：** 你们自己录的测量过程（拍法见第二部分），最后 2 秒切到 `manual_steps.png`，证明和程序的结果一致。

> We measured it ourselves. On NASA SDO images, one per day, we found the edges of the Sun's disk — left at pixel 64, right at 1983 — and so its centre and radius. Then we read the pixel position of two sunspots at very different latitudes, with the exact time as a Julian Date. A program measured every image; we checked it by hand, step by step.

**5b 三角函数和正弦拟合（2:00–2:20）**

**画面：** 你们录的表格计算过程（同样见第二部分），然后 `xy_sine_fit.png`。

> Trigonometry turns pixels into angles: latitude is arcsin of Y; longitude is arcsin of X over cos latitude. Plotted against time, each spot's x position traces a sine wave. The fits give 26.1 days for the spot at 30° north and 25.4 days at 8° south: the Sun's equator spins faster.

**5c 自转方程（2:20–2:35）**

**画面：** `rotation_vs_latitude.png` 左图（21,566 个点组成的云），然后 `rotation_equation.png`。

> Adding 21,566 sunspot groups from 150 years of observatory records, the rotation rates fall on a straight line against sin² latitude: omega equals 14.54 minus 2.84 sin² latitude, in degrees per day.

**5d 蝴蝶图（2:35–2:55）**

**画面：** `differential_rotation_shear.png` 放 3 秒（一条直线被转成螺旋），然后 `butterfly_own.png`，放大最上面那张蝴蝶图。

> This differential rotation winds up the magnetic field — the engine of the cycle. Our own butterfly diagram shows each cycle starting when spots reappear at high latitude: 2008.8 and 2020.0. That's an 11.2-year cycle, pointing to a peak in 2035 to 2036.

**5e 预测（2:55–3:15）**

**画面：** `forecast_v2_ensemble.png`

> Combining fifteen real past cycles into 210 possible futures, the peak lands at 2035.4, plus or minus 1.2 years, with a sunspot number around 156 in 2035. The launch is not before the storm season. It's inside it.

### 6. 结果和建议（3:15–4:40）

**6a 2035 年会遇到什么（3:15–3:40）**

**画面：** `flares_relation.png` 中间那张（X 级耀斑和黑子数），然后 `geomagnetic_storms.png` 右图（高峰后风暴最多）。

> What does 2035 bring? From decades of NOAA and GFZ records: about 30 X-class flares, 11 proton events, and a storm at least as strong as the one that downed the Starlinks one day in four. And storms peak one to three years after the maximum, in the system's first years.

**6b 分层防护（3:40–4:05）**

**画面：** `drag_leo.png` 中间图（从多高出发能撑多少天），然后 `layered_protection.png`，讲到哪一层就放大哪一行。

> No single technology stops that, so we recommend layers. Monitor and warn. Fly higher: deploy at 300 kilometres, not 210 — three weeks of margin instead of two days. A solar-hardened satellite: a ten-kilogram shielded vault around the flight computer, redundant commercial chips, grounding, and a safe mode that turns edge-on and sheds power. Spares in orbit, and ground stations that can run off-grid.

**6c 我们做的工具（4:05–4:15）**

**画面：** `region_calendar.png`

> We also built a tool: from one look at a sunspot region, our rotation law predicts when it will face Earth. For the region behind the May 2024 superstorm, it was right to within a day, five weeks ahead.

**6d 应对手册（4:15–4:25）**

**画面：** `response_playbook.png`

> A response playbook tells each team what to do at each NOAA alert level, and how often to expect it.

**6e 成本（4:25–4:40）**

**画面：** `cost.png`

> The cost: thirteen kilograms per satellite instead of 234 for full hardening — about 80 million dollars a year, six percent of the alternative, and about what one lost batch of satellites costs.

### 7. 结尾（4:40–5:00）

**画面：** 团队出镜。片尾放一张白底字幕，列出数据来源：NASA SDO、NOAA SWPC、WDC-SILSO、GFZ Potsdam、D. Hathaway 的黑子群记录、NRLMSIS 2.1，以及 GitHub 仓库地址。

> Our recommendation: launch in 2035, with these layers built in from the start, and review the forecast as cycle 26 begins around 2030. Some of our satellite numbers are assumptions, and we've said which. But the message is clear: 2035 will be stormy — and the system can be ready.

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

### 剪辑成 25 秒（放在 1:35–2:00）

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

- 三联图（`drag_leo.png`、`geomagnetic_storms.png`、`protons.png`、`rotation_vs_latitude.png`、`flares_relation.png`）宽 2,400–2,550 像素。只放其中一张图时，在剪辑软件里放大到那一块，每块约 800 像素宽，放到 1080p 里依然清楚。
- 不要给图加特效。需要强调某个点时，用一个简单的圆圈或箭头。
- 每张图出现时，台词说的数字要能在图上找到。

## 四、评委可能会问的问题（录之前准备好答案）

工作坊说过："有最好的数据，讲不清、守不住也没用。"

1. **"你们真的自己测了吗？"** 测了两个黑子、7 张图，手动逐步完成，录像可以证明。另外用程序测了 9 个黑子；150 年的方程用的是 D. Hathaway 整理的天文台黑子群记录。
2. **"2035.4 ± 1.2 年准吗？"** 这是 210 种历史组合的分布，不是保证。蝴蝶图法得到 2036.4，13 个周期平均是 2034.8。三种方法都落在 2035 年前后一年里，而发射正好在风暴季里面。2029–2031 年看到第 26 周期的高纬度黑子后，可以把预测收紧。
3. **"为什么不全面加固？"** 每颗卫星要多 234 kg，每年的成本约是我们方案的 16 倍，而且救不了 2022 年那批 Starlink：它们是被大气阻力拖下来的，不是被辐射打坏的。
4. **"成本数字可靠吗？"** 输入都是假设，我们给了高低范围。在整个范围里，分层防护都只要全面加固成本的 5–6%。
5. **"300 km 的依据？"** 用 NRLMSIS 2.1 模型算的，模型先拿 2022 年的事故检验过：算出阻力比之前的发射高约 40%，SpaceX 当时说最多高 50%。

## 五、为什么不要用那份 PDF 报告里的数字

那份报告和仓库对不上，评委一查 GitHub 就会发现：
- 它说用了"2010–2026 年 16 年的 SDO 图像，检测到 253,104 个黑子群"。仓库里没有这个分析。实际上 150 年的自转方程来自 D. Hathaway 的黑子群记录，SDO 图像只有 2014 年 12 月的 7 天。
- 它的加固方案（8 g/cm² 保险箱、剂量从 88.8% 降到 1.0%、20,000 颗卫星、我们的方案 22 亿美元占 2.2%、全面加固 720 亿美元占 72%）来自 `scripts/hardening.py`，仓库里没有这个文件，没法复现，而且和 `cost.py` 的结果不一样。

视频一律用本文和 README 里的数字。
