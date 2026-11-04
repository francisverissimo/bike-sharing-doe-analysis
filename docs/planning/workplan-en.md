# Work Plan for Assignment 2 - Design of Experiments
**Chosen Dataset:** `hour.csv` (UCI Bike Sharing Dataset)

---

## 1. Objective

The objective of this work is to perform a comprehensive and well-founded statistical analysis of the UCI Bike Sharing dataset, applying Design of Experiments (DOE) reasoning to identify factors, levels, effects, and interactions. Based on these findings, we aim to develop a well-justified multiple linear regression model to predict the target response variable.

---

## 2. Understanding the Experimental Design

Since this is an observational (non-experimental) dataset rather than a controlled experiment, we must explicitly describe its underlying structure, as requested in the assignment.

| Aspect | Classification | Justification |
|---|---|---|
| **Type of Study** | Observational (quasi-experimental) | No random assignment of treatments was performed by the researchers. Variables such as weather, day of the week, and season occur naturally. |
| **Design Structure** | Natural factorial design | Several factors act simultaneously on the response variable. This justifies investigating **interactions** (e.g., `workingday * hr`), which would be missed by a one-factor-at-a-time (OFAT) approach. |
| **Between/Within-Subjects** | Primarily between-observations with a temporal structure | Each record corresponds to a specific hour and is not a repeated measurement of the same subject under controlled treatments. However, observations are **sequential over time**, which may introduce temporal autocorrelation. |
| **Randomization** | Not present | The data were collected from the real operation of the Capital Bikeshare system in Washington D.C. during 2011–2012. This must be explicitly stated. |
| **Experimental Unit** | Time interval | For `hour.csv`, each observation represents **one hour on a given calendar day**. |
| **Replications/Blocks** | None planned | No controlled blocking is present. Days could be considered implicit grouping units, but the structure does not correspond to a balanced, planned DOE. |

**Choice of Dataset:** We will use **`hour.csv`** (17,379 observations) because it includes the `hr` (hour of day) variable, which is essential to capture hourly demand patterns and to properly explore factor interactions. `day.csv` (731 observations) would not allow this level of analysis.

---

## 3. Variables: Factors, Levels, Categories, and Response

### 3.1 Response Variable (Y)

- **`cnt`**: Total number of bike rentals (`casual + registered`).
- **Note:** `casual` and `registered` will **not** be used as predictors, as they are components of the response.

### 3.2 Categorical Factors

| Factor | Type | Levels/Categories | Purpose in Analysis |
|---|---|---|---|
| `season` | Categorical (nominal) | 1 = Spring, 2 = Summer, 3 = Fall, 4 = Winter | Seasonal effects. Useful for ANOVA, main effects plots, and regression modeling. |
| `yr` | Categorical (binary) | 0 = 2011, 1 = 2012 | Control factor (system growth between the two years). |
| `mnth` | Categorical (ordinal) | 1–12 | Finer seasonal variation. May be redundant with `season`, so it will be evaluated during screening. |
| `hr` | Categorical | 0–23 (24 levels) | **Key factor.** Critical for analyzing its interaction with `workingday`. |
| `holiday` | Categorical (binary) | 0 = Not a holiday, 1 = Holiday | Low frequency. Its relevance will be assessed in the screening phase. |
| `weekday` | Categorical | 0–6 (Sunday–Saturday) | Day-of-week effect. Partially captured by `workingday`, so potential redundancy will be checked. |
| `workingday` | Categorical (binary) | 0 = Weekend or holiday, 1 = Working day | **Key factor.** Differentiates functional (commute-based) from recreational demand. |
| `weathersit` | Categorical (ordinal) | 1 = Clear/Partly cloudy, 2 = Mist/Cloudy, 3 = Light rain/Thunderstorm, 4 = Heavy rain/Ice/Snow/Fog | Level 4 is extremely rare in this dataset. Therefore, we will restrict our analysis to **levels 1–3**. This factor is well-suited to assess the impact of adverse weather. |

### 3.3 Numerical Variables (Covariates)

| Variable | Range (normalized) | Proposed Treatment |
|---|---|---|
| `temp` | ~0–1 (approx. -8 °C to 33 °C) | Strong predictor. For **ANOVA and DOE plots**, we may discretize into ranges (Low/Medium/High). For **multiple regression**, it will remain **continuous**. |
| `atemp` | 0–1 (feeling temperature) | **Highly correlated with `temp`**. To avoid multicollinearity, we will use **only `temp`**, clearly justifying this choice. |
| `hum` | 0–1 (relative humidity) | Potential moderate effect, often linked to weather conditions. Will be evaluated during screening and modeling. |
| `windspeed` | 0–1 (wind speed) | Expected small-to-moderate effect. Will be included in the initial screening. |

---

## 4. Hypotheses for Effects and Interactions (DOE Reasoning)

### 4.1 Expected Main Effects

| Factor | Expected Strength | Rationale |
|---|---|---|
| `hr` | **Very strong** | Working days show a bimodal pattern (morning/evening commute), while non-working days show a smoother, more unimodal recreational pattern. |
| `workingday` | **Strong** | Distinguishes mandatory trips from discretionary/recreational trips. |
| `weathersit` | **Strong** | Adverse weather conditions are expected to significantly reduce bike demand. |
| `season` / `temp` | **Strong** | Higher demand in warmer seasons; lower in winter. `temp` captures this thermal effect directly. |
| `temp` | **Moderate–Strong** | Likely curvilinear: demand increases up to a comfort range, then may level off or decrease at very high temperatures. |
| `hum` | **Moderate** | High humidity is often associated with less comfortable or rainy conditions. |
| `windspeed` | **Weak–Moderate** | Strong wind is expected to discourage bike usage. |
| `weekday` | **Moderate** | Largely overlapping with `workingday`. |
| `holiday` | **Weak** | Few holiday observations in the dataset. |
| `yr` | **Moderate** | Natural growth of the bike-sharing system from 2011 to 2012. |

### 4.2 Key Interactions to Investigate

| Interaction | Rationale | Importance |
|---|---|---|
| **`workingday * hr`** | The hourly profile differs drastically: bimodal on working days vs. unimodal on weekends/holidays. | **Highest priority (must include).** This is the most explanatory interaction for this dataset. |
| **`weathersit * hr`** | Adverse weather may have a stronger negative impact during mandatory commute hours than during flexible leisure hours. | **High.** Will be tested statistically and justified for inclusion/exclusion. |
| **`season * hr`** | Daylight duration and temperature vary by season (e.g., earlier darkness in winter), affecting hourly usage patterns. | Relevant for a more complete DOE perspective. |
| **`workingday * weathersit`** | Commuters on working days may be less sensitive to light rain than recreational users on non-working days. | Interesting behavioral interaction worth investigating. |
| **`temp * hr`** | Perceived comfort depends on time of day (e.g., colder in early morning). | May be considered in the regression model if statistically supported. |
| **`season * temp`** | Possible redundancy, but worth checking: the same temperature may be perceived differently across seasons. | Requires careful assessment due to potential multicollinearity. |

---

## 5. Methodology

We will follow the steps requested: **descriptive analysis**, **detailed statistical analysis (assumptions, transformations, tests, results, conclusions)**, and **development of well-justified predictors**.

### 5.1 Step 1: Exploratory Data Analysis (EDA)

- **Sample size:** Confirm total observations (`n = 17,379`) and breakdown by key factors (`season`, `workingday`, `weathersit`, `yr`).
- **Summary statistics:** Compute mean, median, standard deviation, minimum, maximum, Q1, and Q3 for `cnt`.
- **Distribution analysis:** Histograms, kernel density estimates, skewness, and kurtosis of `cnt`.
- **Comparative plots:** Boxplots of `cnt` by `hr`, `workingday`, `weathersit`, `season`, `weekday`, and `yr`.
- **Time-based visualization:** Plot `cnt` over time to detect trends, seasonal patterns, and year-to-year differences (2011 vs. 2012).
- **Correlation analysis:** Examine Pearson correlations among numerical variables (`temp`, `hum`, `windspeed`, `cnt`).
- **Outlier inspection:** Identify potential outliers via boxplots and residual-based diagnostics. Outliers will not be removed unless strongly justified.

### 5.2 Step 2: Assumptions, Transformations, and Temporal Dependence

| Check | Tools/Tests | Objective |
|---|---|---|
| **Normality** | Shapiro–Wilk (or Kolmogorov–Smirnov), **QQ-plots**, histograms | Assess distributional assumptions, focusing primarily on **model residuals** rather than raw `cnt`. |
| **Homoscedasticity** | Levene/Bartlett tests (by groups), **Residuals vs. Fitted** plot, Scale–Location plot | Verify constant variance, required for valid ANOVA and linear regression. |
| **Independence** | **Durbin–Watson test**, **ACF/PACF** of residuals | **Critical due to temporal data.** We will test, report, and discuss potential autocorrelation as an inherent limitation of this observational time series. |
| **Response Transformation** | Box–Cox procedure, evaluate `sqrt(cnt)` and `log(cnt + 1)` | Improve compliance with assumptions if necessary. The final decision (apply or not) will be explicitly justified, weighing assumption validity against interpretability. |
| **Influential Observations** | Cook's Distance, leverage, studentized residuals | Detect high-leverage/influential points and assess their impact without arbitrary deletion. |

### 5.3 Step 3: DOE Analysis – Effects, Interactions, and ANOVA

| Analysis | Approach | Purpose |
|---|---|---|
| **Initial Screening** | Evaluate factor relevance using exploratory plots and summary comparisons. | Focus on the most influential factors aligned with DOE reasoning. |
| **Main Effects Plots** | Generate for `workingday`, `hr`, `weathersit`, `season`, `temp` (discretized), `hum`, `windspeed`. | Visualize the magnitude and direction of main effects (classical DOE view). |
| **Interaction Plots** | Prioritize **`workingday * hr`**, then `weathersit * hr`, `season * hr`, `workingday * weathersit`. | Detect and interpret interaction patterns (e.g., non-parallel lines). |
| **One-Way ANOVA** | Test `cnt ~ workingday`, `cnt ~ weathersit`, `cnt ~ season`. | Assess whether mean differences across factor levels are statistically significant. |
| **Factorial ANOVA (with Interactions)** | Fit models including main effects and interaction terms, focusing on `workingday + hr + workingday:hr`. | Statistically support the effects/interactions observed in plots – directly linking to DOE methodology. |
| **Post-Hoc Tests** | **Tukey HSD** when ANOVA is significant. | Perform pairwise comparisons between levels (e.g., for `season`, `weathersit`, or grouped `hr` categories). |

### 5.4 Step 4: Multiple Regression Modeling (Developing a Justified Predictor)

Using insights from Step 3, we will build a sequence of regression models, adding complexity only when statistically and theoretically justified.

| Model | Specification | DOE-Based Justification |
|---|---|---|
| **M0 – Baseline (Main Effects)** | `cnt ~ workingday + hr + weathersit + temp + season + yr + hum + windspeed` | Includes the strongest main effects identified during screening. |
| **M1 – Core Interaction** | **M0 + `workingday * hr`** | **Essential.** Captures the fundamental difference between hourly demand profiles of working vs. non-working days. |
| **M2 – Additional Interactions** | **M1 + `weathersit * hr`** (optionally `season * hr`) | Tests whether weather impact varies by hour. Will be retained only if significant and meaningful for interpretation. |
| **M3 – Curvilinearity** | **M2 + `temp^2`** (consider `hum^2` if warranted) | Accounts for the expected non-linear effect of temperature (comfort range). Inclusion requires statistical support. |
| **M4 – Parsimonious Final Model** | Reduced version retaining only terms justified by significance, VIF, AIC/BIC, and domain logic. | Achieves a balance between fit, simplicity, and interpretability. Any term removed will be explicitly justified. |

### 5.5 Step 5: Model Comparison, Diagnostics, and Validation

| Criterion | Tool/Metric | Application |
|---|---|---|
| **Explained Variance** | $R^2$ and **Adjusted $R^2$** | Evaluate goodness-of-fit. Adjusted $R^2$ is preferred to penalize unnecessary complexity. |
| **Model Comparison** | **AIC and BIC** | Objectively compare nested and competing models. |
| **Multicollinearity** | **Variance Inflation Factor (VIF)** | Check for high collinearity, especially among `temp`, `season`, and `mnth`. If detected, we will justify removing redundant predictors. |
| **Regression Diagnostics** | Residuals vs. Fitted, QQ-plot, Scale–Location, Cook's Distance, Leverage, Studentized Residuals | Verify key assumptions: linearity, homoscedasticity, normality of residuals, and influential observations. |
| **Temporal Validation (Hold-Out)** | **Train/Test Split by Year:** Train on 2011 (`yr=0`), Test on 2012 (`yr=1`) | More appropriate than random CV for time-dependent data. Avoids temporal leakage and better reflects real-world generalization. |
| **Test Performance Metrics** | **RMSE, MAE, MAPE** (where meaningful) | Quantify predictive accuracy on the unseen 2012 test set. |
| **Model Selection Principle** | Holistic evaluation | The final "predictor" will be the **most well-justified model** (fit + statistical significance + DOE coherence + parsimony), not simply the one with the highest $R^2$. |

---

## 6. Paper Structure (SBC Format, 6–12 pages)

The final report will be written in **English** following the Brazilian Computer Society (SBC) format.

| Section | Required Content |
|---|---|
| **Title** | Clear and representative (e.g., *"Statistical Analysis and Demand Prediction for Bike Sharing: A DOE-Based Approach"*). |
| **Abstract** | Objective, dataset, methodology (DOE + regression), main findings, and conclusions (150–250 words). |
| **1. Introduction** | Context, relevance, objectives, and rationale for combining DOE with predictive modeling. |
| **2. Dataset and Experimental Design** | Data source (UCI), variable descriptions, factors/levels/response, detailed design classification (observational, factorial, between/within, randomization), experimental unit, and limitations (temporal structure). |
| **3. Methodology** | EDA, assumptions, transformations (with justification), statistical tests (ANOVA, post-hoc), main effects & interaction plots (DOE), multiple regression, model selection, diagnostics, and temporal validation. |
| **4. Results** | Descriptive statistics, plots (boxplots, histograms, main effects, interaction plots), ANOVA results, model tables (coefficients, p-values, AIC/BIC, $R^2$/Adjusted $R^2$), diagnostics, and train/test performance. |
| **5. Discussion** | **Interpretation of main effects and interactions** from a DOE perspective, model comparison, **explicit justification for the chosen predictor** (fit, significance, theoretical coherence, parsimony), practical implications, and discussion of temporal dependence/limitations. |
| **6. Conclusion** | Key findings, most influential factors, most well-justified model, study limitations, and suggestions for future work. |
| **References** | Mandatory citation of Fanaee-T & Gama (2013): *"Event labeling combining ensemble detectors and background knowledge"*, Prog. Artif. Intell., Springer. Also cite the UCI Bike Sharing Dataset. |
| **Appendix (Optional)** | Supplementary tables, full statistical outputs, additional plots, and detailed diagnostics. |

---

## 7. Timeline (As per Assignment)

| Date | Task |
|---|---|
| **October 26th, 2026** | **Deadline:** Submit ideas, materials, and methods (dataset, planned work, methodology) to the professor by email. |
| **November 22nd, 2026** | **Submission:** Upload the complete final work. |
| **November 23rd, 2026** | **Presentation:** Oral presentation of the assignment. |

---

## 8. Final Notes

1. **Justification-driven approach:** Every decision (factor selection, interaction inclusion/exclusion, transformation, final model choice) will be backed by statistical evidence and solid DOE reasoning.
2. **Focus on the key interaction:** The `workingday * hr` interaction will be thoroughly explored (plots + ANOVA + regression) as it best demonstrates the value of a DOE perspective.
3. **Addressing temporal dependence:** Autocorrelation will be explicitly tested (Durbin–Watson, ACF/PACF) and its implications discussed, reflecting methodological rigor.
4. **Bonus (dataset publication):** The dataset is already publicly available on UCI with proper citation. Optionally, we may publish our organized code, processed data, and materials in a public repository (GitHub/Zenodo) to fulfill the bonus suggestion.
