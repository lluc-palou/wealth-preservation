# Fiat Debasement and Wealth Allocation: BTC, Gold, Equities and USD Cash

## 1. Research Question

The central question addressed in this analysis is whether Bitcoin (BTC) constitutes a superior store of wealth compared to holding USD cash, in the context of ongoing fiat currency debasement, and how its performance as a debasement hedge compares to gold and US equities. The analysis covers monthly data from approximately 2015 to 2025, focusing on the US monetary system as the primary debasement reference.

The question is decomposed into two sub-questions: first, whether the long-run real returns of BTC, gold, and equities have historically exceeded those of USD cash; and second, whether observable debasement conditions (as measured by monetary and inflation indicators) reliably predict periods of asset outperformance over cash.

---

## 2. Data and Methodology

All data were sourced at the highest available frequency: macroeconomic series (M2 money supply, CPI, GDP, Federal Funds rate, and 10-year TIPS real yield) from the Federal Reserve Economic Data (FRED) database, and market price series (BTC-USD, S&P 500, gold futures) from Yahoo Finance. Given that the binding constraints of the dataset are M2 at monthly frequency and BTC data beginning in late 2014, all series were aligned to a common monthly frequency (daily series sampled at month-end, quarterly GDP interpolated to monthly using cubic spline) and restricted to the common date range, yielding approximately 119 monthly observations.

The analytical framework rests on a return spread formulation: for each asset, the monthly log return in excess of the real USD cash return (approximated as the Fed Funds rate minus CPI YoY inflation, divided by twelve) is computed. These spreads directly measure whether holding a given asset preserved purchasing power better than holding fiat cash in a given month. Debasement pressure is characterized through four indicators (M2 YoY growth, CPI YoY inflation, real M2 growth as M2 minus CPI, and the M2/GDP ratio), which are combined into composite scores via z-score averaging and Principal Component Analysis (PCA), both of which are compared for robustness. The regression framework regresses each asset's monthly spread against PCA components and the TIPS real yield, with Newey-West HAC standard errors (12 lags) to correct for autocorrelation and heteroskedasticity.

---

## 3. The Debasement Environment: 2015–2025

The four debasement indicators reveal a sample dominated by one exceptional episode and two structurally distinct regimes, as shown in Figure 1.

![Raw Debasement Indicators](debasement_indicators_raw.png)
*Figure 1. Raw debasement indicators on a monthly basis, 2015–2025.*

The 2015–2019 period constitutes a stable low-debasement baseline: M2 YoY growth oscillated between 3% and 7%, CPI remained anchored between 1% and 2.5%, and the M2/GDP ratio drifted slowly from 0.67 to 0.70. The COVID-19 monetary response in 2020 produced the most significant debasement impulse in the sample, with M2 YoY growth reaching approximately 26% by early 2021 and the M2/GDP ratio jumping to 0.87 almost vertically, driven by unprecedented fiscal transfers and Federal Reserve asset purchases. Critically, CPI did not respond until mid-2021, peaking at approximately 9% in mid-2022 (some 12–18 months after the monetary expansion peak), which reflects the well-documented transmission lag between money supply growth and realized consumer price inflation.

The 2022–2023 period is the most analytically challenging: M2 contracted year-on-year for the first time in modern history (reaching approximately -5%), and real M2 growth fell to nearly -10%, signaling aggressive monetary tightening; yet CPI simultaneously recorded its highest readings of the entire sample. This divergence (where quantity-based and price-based debasement indicators point in opposite directions) is precisely the tension that motivates a multivariate decomposition of the debasement signal. By 2024–2025, all indicators had returned toward the pre-2020 baseline, though M2/GDP remained structurally elevated at approximately 0.72, indicating that the monetary expansion of 2020 was never fully unwound.

---

## 4. Purchasing Power Preservation: Descriptive Results

### 4.1 Cumulative Real Returns

The cumulative return comparison (Figure 2) provides the most direct descriptive answer to the wealth allocation question.

![Cumulative Returns](cumulative_returns_comparison.png)
*Figure 2. Cumulative returns on a log scale (base = 1 at start), 2015–2025.*

Over the full sample, BTC delivered approximately 400–500x cumulative return from the 2015 base, while both S&P 500 and gold converged toward approximately 3x, and real USD cash return remained at or marginally below 1.0 throughout. The dominance of BTC is unambiguous on a log scale, but its path structure is equally important: virtually all cumulative outperformance was generated in three discrete episodes (the 2017 bubble, the 2020–2021 QE rally, and the 2024–2025 halving cycle), with intervening drawdowns of 60–80% from each peak. USD cash, by contrast, exhibited near-zero real return for the decade, with only a marginal recovery in 2022–2023 when the Fed Funds rate temporarily exceeded CPI inflation. Gold and equities both consistently beat cash by a modest margin across the full period, with gold catching up to equities sharply in 2024–2025, likely driven by central bank demand and geopolitical risk premia that are independent of US monetary debasement dynamics.

### 4.2 Monthly Spread Distributions

Examining monthly return spreads versus real cash (Figure 3) reveals the frequency and consistency of outperformance at a granular level.

![Return Spreads vs Cash](return_spreads_vs_cash.png)
*Figure 3. Monthly return spreads versus real USD cash for BTC, gold, and S&P 500.*

BTC's spread oscillates between approximately -0.50 and +0.50, with green (outperforming) months dominating in count but with negative months of comparable magnitude to positive ones. The implication is that BTC's long-run edge over cash is delivered through a small number of very large positive months rather than through consistent modest outperformance, which is a buy-and-hold property rather than a tactical one. Gold presents the most balanced and controlled profile: the spread band is narrow (approximately ±0.10), negative months are shallow, and the ratio of positive to negative months is consistently favorable across all subperiods. S&P 500 exhibits a structural shift post-2020, with the spread turning persistently positive once the zero interest rate environment made virtually any positive equity return superior to cash yield.

---

## 5. Is Debasement a Reliable Signal? Regression Results

### 5.1 PCA Structure of the Debasement Signal

PCA applied to the four standardized debasement indicators yields two components which together explain 97.6% of total variance (PC1: 59.1%, PC2: 38.5%), confirming that the debasement phenomenon in this sample is fundamentally two-dimensional rather than one-dimensional, which justifies the multivariate regression specification.

PC1 loads heavily on M2 YoY growth (+0.646), real M2 growth (+0.623), and M2/GDP (+0.424), with CPI nearly absent (-0.126). It captures the **monetary expansion impulse**: the period when the printing press runs, before prices respond. PC2 loads primarily on CPI (+0.777) and M2/GDP (+0.586), with real M2 growth loading negatively (-0.228). It captures the **debasement transmission phase**: when monetary expansion has already propagated into realized consumer prices while the structural ratio remains elevated, corresponding precisely to the 2022 inflation regime. The correlation between the PCA-derived PC1 score and the z-score composite debasement score is 0.866, confirming broad alignment between the two methods, though the divergence (attributable to CPI's differential weighting) is meaningful around the 2022 episode and motivates the use of PCA as the primary specification.

### 5.2 Debasement Score vs. Asset Spreads: Visual Inspection

Figure 4 overlays the z-score composite debasement score against 12-month rolling mean spreads for each asset.

![Debasement Score vs Spreads](debasement_score_vs_spreads.png)
*Figure 4. Z-score composite debasement score vs. 12-month rolling spread per asset.*

Gold exhibits the most visually coherent alignment with the debasement score: both series rise together through 2020–2021 and decline together into 2022–2023. BTC shows partial alignment in 2020–2021 but had already generated strong positive spreads in 2016–2017 when the debasement score was near zero or negative, indicating autonomous price dynamics independent of monetary conditions. S&P 500's co-movement with the debasement score in 2020–2021 reverses sharply in 2022 when the tightening cycle crushed equities despite inflation still running hot, suggesting that equities respond to the liquidity dimension of debasement rather than to the inflation dimension. The post-2023 divergence, where BTC and gold spreads recover while the debasement score remains subdued, further indicates that forces beyond monetary debasement (the Bitcoin halving cycle, central bank gold demand) are driving recent asset performance.

### 5.3 Full Sample Regression

The full sample OLS regression with Newey-West HAC standard errors (12 lags) produces the results summarized in Table 1.

| Regressor | BTC coef. | BTC p-val. | Gold coef. | Gold p-val. | S&P 500 coef. | S&P 500 p-val. |
|---|---|---|---|---|---|---|
| PC1 (Monetary Expansion) | +0.0249 | 0.094 | +0.0001 | 0.967 | +0.0050 | 0.105 |
| PC2 (Realized Inflation) | **-0.0348** | **0.003** | -0.0005 | 0.795 | -0.0024 | 0.262 |
| TIPS Real Yield (10Y) | +0.0143 | 0.476 | +0.0020 | 0.697 | +0.0025 | 0.596 |
| **R²** | **0.071** | | **0.003** | | **0.024** | |

*Table 1. Full sample regression results. Bold entries denote statistical significance at the 5% level.*

The results constitute a broad null finding: debasement conditions, as measured by PC1, PC2, and TIPS real yield, explain a negligible fraction of monthly return spread variance for gold (R² = 0.003) and equities (R² = 0.024), and only 7.1% for BTC. The single statistically significant coefficient across all three assets is PC2 for BTC (p = 0.003), with a negative sign: periods of elevated realized inflation and high M2/GDP ratio are associated with BTC *underperforming* cash, not outperforming it. This result is economically interpretable: the realized inflation phase (2022) triggered aggressive Fed tightening, which crushed BTC as a risk asset. The PC1 coefficient for BTC is positive (+0.025) and marginally significant at the 10% level (p = 0.094), providing at best weak directional support for the monetary expansion channel. The TIPS real yield is insignificant for all three assets after controlling for the PCA components, which is expected given its -0.79 correlation with PC1, as the two variables share the same underlying monetary cycle information.

### 5.4 Subsample Stability and Rolling Regression

The subsample analysis reveals substantial instability in the PC1 coefficient across the pre- and post-2020 structural break. For BTC, the pre-2020 coefficient (+0.055) collapses to +0.009 post-2020, representing an 84% reduction in magnitude. Gold's coefficient reverses sign between subsamples (-0.083 pre-2020 to -0.010 post-2020), canceling to near zero in the full sample. This instability implies that full-sample coefficients are averages of structurally different regimes and carry limited economic meaning as structural parameters.

The rolling 36-month PC1 coefficient (Figure 5) makes this structural disappearance explicit.

![Rolling PC1 Coefficient](rolling_pc1_coefficient.png)
*Figure 5. Rolling 36-month PC1 coefficient for each asset, with 95% confidence bands. Green shading indicates periods of statistical significance.*

For BTC, the coefficient was positive and economically meaningful (approximately +0.25 to +0.35) through 2018–2020, then collapsed sharply to near zero by 2021 and has remained there with a narrowing confidence band, confirming that the near-zero post-2021 estimate is not uncertainty but a precise structural null. Gold's rolling coefficient oscillates around zero throughout the entire sample, never departing in a sustained manner. S&P 500 shows a brief negative excursion in early 2020 (the simultaneous debasement surge and COVID crash) before reverting to zero. The pattern for BTC is consistent with a relationship that existed in the early adoption phase of the asset but has since disappeared as BTC's price dynamics became dominated by halving cycles, institutional adoption flows, and macro risk-on/risk-off behavior.

### 5.5 Regime Analysis

Splitting the sample at the PC1 median into high-debasement and low-debasement regimes and comparing mean spreads via Welch t-tests yields no statistically significant difference for any asset (BTC: p = 0.195; Gold: p = 0.595; S&P 500: p = 0.794), as visualized in Figure 6.

![Regime Boxplots](regime_spread_boxplots.png)
*Figure 6. Monthly return spread distributions by debasement regime (PC1 median split).*

BTC's high-debasement box is visually elevated relative to the low-debasement box, with a mean spread difference of +0.047, but BTC's extreme idiosyncratic variance (evident in the wide interquartile ranges of both boxes) precludes statistical detection with the available sample size. Gold and S&P 500 boxes are nearly indistinguishable across regimes, with differences of -0.004 and +0.002 respectively.

---

## 6. Conclusions

The analysis yields several clear findings, which are stated directly below.

**BTC has dramatically outperformed USD cash in purchasing power terms over the full sample (2015–2025), delivering approximately 400–500x cumulative return versus near-zero real cash return.** This result is robust and unambiguous. However, it is delivered episodically through three discrete price rallies separated by severe drawdowns of 60–80%, requiring buy-and-hold discipline over multi-year horizons rather than tactical allocation.

**Gold and equities have both modestly and consistently beaten cash at approximately 3x cumulative real return over the same period.** Gold's outperformance is more consistent month-to-month with lower volatility; equity outperformance is structurally tied to the interest rate environment, becoming pronounced in the zero-rate post-2020 period.

**Debasement conditions do not reliably predict monthly asset outperformance over cash for any of the three assets at the frequency and horizon examined.** The regression analysis finds no statistically significant positive relationship between the monetary expansion component (PC1) and any asset's spread over cash. R² values of 0.003 for gold and 0.024 for equities confirm that debasement indicators carry negligible information about which months those assets will beat cash.

**The only statistically significant debasement-related coefficient is negative: realized inflation pressure (PC2) predicts BTC underperforming cash.** This finding inverts the naive debasement hedge thesis, as BTC is hurt by the tightening cycle that follows inflation, confirming that it behaves primarily as a risk asset rather than an inflation hedge in the short run.

**The relationship between debasement conditions and BTC's outperformance, which existed in the 2017–2020 period, has structurally disappeared post-2021.** The rolling regression demonstrates this collapse precisely, with the PC1 coefficient for BTC declining from approximately +0.30 to near zero and remaining there. This structural break is the most important single finding of the quantitative analysis.

**For a wealth allocator concerned with fiat debasement, the practical implication is a buy-and-hold allocation to BTC and gold rather than a debasement-timing strategy.** The long-run case for both assets over cash is supported by the data; the case for using observable debasement metrics to time entries and exits is not.

---

### Limitations

Several limitations of this analysis warrant acknowledgment. The BTC sample of approximately 119 monthly observations, heavily influenced by three bull market episodes, provides limited statistical power to detect modest but persistent debasement effects that may operate at longer horizons. The confounding of monetary debasement with liquidity cycles (both of which peaked simultaneously in 2020–2021) makes causal attribution inherently difficult at the frequencies examined. Furthermore, the post-2023 divergence between gold's strengthening performance and the normalized debasement score suggests that factors beyond US monetary policy (geopolitical risk, central bank gold accumulation, the Bitcoin halving mechanism) are increasingly relevant drivers that fall outside the scope of this framework.
