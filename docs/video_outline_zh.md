# 五分钟视频大纲

给 ISECG 发射评审团的视频，用英文讲。下面每段写了时间、画面（用哪张图）和英文台词。台词约 700 词，按每分钟 140–150 词的语速约 5 分钟，录之前先计时练一遍，超时就删减第 5 段。

图片路径都在 `figures/` 下：`figures/video/` 里是 16:9 的视频图，其余是普通分析图，放进视频时可以裁剪或放大其中一块。

## 1. 开场（0:00–0:20）

**画面：** `video/v01_cover.png` 2 秒，然后 `video/v02_incidents.png`，在剪辑软件里把 2022 年 Starlink 那个点圈出来。

> February 2022: a minor solar storm brought down 38 brand-new Starlink satellites. In 2035 the Sun will be near its peak, and ISECG is launching anyway. We forecast what 2035 will bring, and designed layered, low-cost protection for a satellite constellation.

## 2. 数学：测黑子和自转（0:20–1:25）

**0:20–0:40 画面：** `video/v05_step1_measure.png`，加队员手动量黑子的镜头。可以把 `data/sdo/` 里 7 张原图按顺序放成 2 秒延时，能看到黑子在移动。

> We tracked sunspots on NASA SDO images, one per day. On every image we measured the disk edges, its centre and radius, and each spot's pixel position and Julian Date. A program measured all the images; we checked it by hand, step by step, on two spots: A at 30° north and E at 8° south.

**0:40–0:55 画面：** `video/v06_step2_trigonometry.png`

> Trigonometry turns pixels into angles: latitude = arcsin Y, longitude = arcsin(X ÷ cos latitude). Spot A moved 63.8° in 5 days. Add Earth's own orbital motion, and the Sun turns once in 26.1 days.

**0:55–1:10 画面：** `video/v07_step2_sine_fit.png`，再闪 2 秒 `xy_sine_fit.png`（题目要求画 x 和 y 两条，这张两条都有）。

> Each spot's x position traces a sine wave; the fitted period gives 26.1 days for A and 25.4 days for E. The equator spins faster.

**1:10–1:25 画面：** `video/v08_step2_equation.png`

> From 21,566 sunspot groups over 150 years we derived the law: ω = 14.54 − 2.84 sin² latitude, in degrees per day — assuming a spherical Sun whose rotation depends only on latitude.

## 3. 蝴蝶图和预测（1:25–2:05）

**画面：** `differential_rotation_shear.png` 3 秒，然后 `video/v03_butterfly.png`，再 `video/v04_forecast.png`。

> This differential rotation winds up the Sun's magnetic field — the engine of the solar cycle. Our own butterfly diagram, from 3,779 sunspot groups, shows each new cycle starting when spots reappear at high latitude: 2008.8 and 2020.0. That's an 11.2-year cycle, so cycle 26 starts around 2031 and peaks in 2035–36. Combining 15 real past cycles into 210 possible futures puts the maximum at 2035.4 ± 1.2 years, with a sunspot number around 156 in 2035. Our launch sits right on the peak.

## 4. 风险识别（2:05–2:50）

**画面：** `video/v10_flares_vs_sunspots.png`，然后 `video/v14_storms_after_maximum.png`，最后 `drag_leo.png`（裁出左边的密度图）。时间够的话闪一下 `protons.png`。

> What does that mean? More sunspots, more flares: about 30 radio blackouts in 2035, and all 12 past years this active had at least one. For satellites in low Earth orbit, the bigger threat is geomagnetic storms: a storm as strong as the one that downed the Starlinks is expected one day in four, and storms peak 1–3 years after maximum. We fed our forecast into the NRLMSIS atmosphere model: at 550 km the air in 2035 is 14 times denser than at solar minimum — even a quiet 2035 day beats the 2022 storm day.

## 5. Curveball：五层防护和成本（2:50–4:15）

**画面：** 先放 `layered_protection.png` 全表，讲到哪一层就放大哪一行。

> No single technology stops space weather, so we protect in five layers, and only spend mass where it matters.

**第 1 层，画面：** `region_calendar.png`，再 `video/v12_risk_calendar.png`

> Layer 1, forecasting tools. Our rotation law becomes a calendar: from one look at the region behind the May 2024 superstorm, it predicted every date — even its return a month later — to within a day. We add a yearly risk calendar, and deploy only when three calm days are forecast; in years like 2035, more than half of all 3-day stretches are storm-free.

**第 2 层，画面：** `drag_leo.png` 的中间和右边两张

> Layer 2, orbit: deploy at 300 km or higher, not 210 — in safe mode a satellite then survives 19 to 33 days instead of 2 to 3 — and operate near 550 km, where staying up costs about 1 kg of fuel a year.

**第 3 层，画面：** `layered_protection.png` 放大第 3 行，加 NASA 的 Juno 辐射保险箱照片（NASA 公开图片）

> Layer 3, a solar-hardened satellite, not a fully hardened one: fly edge-on in storms; put only the flight computer and power control in a 10 kg liquid-cooled, shielded vault, as NASA did on Juno; use commercial chips with triple redundancy and error correction; ground every surface against charging.

**第 4、5 层，画面：** `layered_protection.png` 第 4、5 行；`video/v02_incidents.png` 放大 1989 年魁北克那个点

> Layers 4 and 5: spares in orbit — dead satellites burn up within about 1.4 years at solar maximum — and ground stations that can run off-grid, the lesson of Québec 1989.

**成本，画面：** `cost.png`

> The cost: our layers add 13 kilograms per satellite; full hardening would add 234. That is about 80 million dollars a year instead of 1.3 billion — the price of one lost batch of satellites, and under 0.1% a year of the 100-billion-dollar system. And hardening would not have saved the 2022 Starlinks: drag killed them, not radiation.

## 6. 应对手册和决定（4:15–4:40）

**画面：** `response_playbook.png`，然后一条检查点时间线（PPT 里画：2029–31、2030、2031、发射前一个月、发射当天）。

> Our response playbook links NOAA alerts to actions: G1–2 — hold deployments; G3 — low-drag attitude, pause manoeuvres; G4–5 or strong radiation storms — full safe mode and backup power; afterwards — raise sunken satellites and launch spares. Our recommendation: go in 2035, with these layers and checkpoints from 2029 onwards.

## 7. 局限和结尾（4:40–5:00）

**画面：** 团队出镜，或回到封面；片尾列出数据和图片来源。

> Our forecast is built from real past cycles, so we'll update it every year, and some satellite numbers are assumptions. But the message is clear: 2035 will be stormy — and with layered, low-cost protection, the system can ride it out. Thank you.

## 每条要求在视频里的位置

| 要求 | 时间 |
|---|---|
| 1. 追踪两个不同纬度的黑子，记录像素坐标和儒略日 | 0:20–0:40 |
| 2. 三角函数求周期；画 x、y 随时间变化，拟合正弦 | 0:40–1:10 |
| 3. 推导自转方程，说明假设 | 1:10–1:25 |
| 4. 自己画蝴蝶图，量出周期，找到下一个高峰 | 1:25–1:50 |
| 5. 预测 2035 年，和真实无线电中断对照 | 1:50–2:20 |
| 6. 防护方案：发射时机、轨道设计、硬件屏蔽、地面电网 | 第 1、2、3、5 层 |
| 7. 向 ISECG 陈述，展示数学、蝴蝶图和决定 | 全片；决定在 4:15 |
| Curveball：抗太阳风暴卫星、不做全面加固、经济地保护 1000 亿美元系统 | 2:50–4:15 |
| 第二次工作坊"风险识别"：运行准备和应对工具、分层防护 | 第 1 层、5 层表、4:15 的应对手册 |

## 录制提醒

- 视频里的数字要和 README 完全一致。
- 一定要拍手动测量的镜头，配合 0:20 那句"程序量全部图像，我们手动逐步检查两个黑子"，这样说才是真实的。
- 用到的照片优先选 NASA 的公开图片，片尾注明所有图片和数据的来源。
