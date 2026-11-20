"""Build the reproducible English slide deck for the bike-sharing analysis."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "presentation" / "bike-sharing-analysis.pptx"
FIGURES = ROOT / "outputs" / "figures"
DIAGNOSTICS = ROOT / "outputs" / "diagnostics"

SLIDE_WIDTH = 13.333
SLIDE_HEIGHT = 7.5
FONT = "Arial"
MONO = "Consolas"

NAVY = RGBColor(15, 23, 42)
BLUE = RGBColor(29, 78, 216)
TEAL = RGBColor(15, 118, 110)
ORANGE = RGBColor(234, 88, 12)
GRAY = RGBColor(100, 116, 139)
LIGHT = RGBColor(241, 245, 249)
WHITE = RGBColor(255, 255, 255)
BORDER = RGBColor(203, 213, 225)


def style_frame(
    frame: object,
    size: float,
    color: RGBColor,
    *,
    bold: bool = False,
    font: str = FONT,
    align: PP_ALIGN = PP_ALIGN.LEFT,
) -> None:
    """Apply a consistent typographic style to every paragraph in a text frame."""
    frame.word_wrap = True
    frame.margin_left = 0
    frame.margin_right = 0
    frame.margin_top = 0
    frame.margin_bottom = 0
    for paragraph in frame.paragraphs:
        paragraph.alignment = align
        for run in paragraph.runs:
            run.font.name = font
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color


def add_text(
    slide: object,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    *,
    size: float = 18,
    color: RGBColor = NAVY,
    bold: bool = False,
    align: PP_ALIGN = PP_ALIGN.LEFT,
    font: str = FONT,
    valign: MSO_ANCHOR = MSO_ANCHOR.TOP,
) -> object:
    """Add a styled text box positioned in inches."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.text = text
    frame.vertical_anchor = valign
    style_frame(frame, size, color, bold=bold, font=font, align=align)
    return box


def add_bullets(
    slide: object,
    x: float,
    y: float,
    w: float,
    h: float,
    items: list[str],
    *,
    size: float = 17,
    color: RGBColor = NAVY,
    gap: float = 9,
) -> object:
    """Add a manually bulleted list with consistent spacing."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    frame = box.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.margin_left = 0
    frame.margin_right = 0
    frame.margin_top = 0
    frame.margin_bottom = 0
    for index, item in enumerate(items):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.text = f"•  {item}"
        paragraph.space_after = Pt(gap)
        for run in paragraph.runs:
            run.font.name = FONT
            run.font.size = Pt(size)
            run.font.color.rgb = color
    return box


def add_rect(
    slide: object,
    x: float,
    y: float,
    w: float,
    h: float,
    fill: RGBColor,
    *,
    line: RGBColor | None = None,
    rounded: bool = False,
) -> object:
    """Add a filled rectangle, optionally rounded and outlined."""
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(0.75)
    return shape


def add_table(
    slide: object,
    x: float,
    y: float,
    w: float,
    h: float,
    data: list[list[str]],
    *,
    widths: list[float] | None = None,
    font_size: float = 12,
    aligns: list[PP_ALIGN] | None = None,
) -> object:
    """Add an explicitly styled table with a highlighted header row."""
    rows, columns = len(data), len(data[0])
    shape = slide.shapes.add_table(rows, columns, Inches(x), Inches(y), Inches(w), Inches(h))
    table = shape.table
    table.first_row = False
    table.horz_banding = False
    if widths:
        total = sum(widths)
        for index, width in enumerate(widths):
            table.columns[index].width = Inches(w * width / total)
    for row in table.rows:
        row.height = Inches(h / rows)
    for row_index, row in enumerate(data):
        for col_index, value in enumerate(row):
            cell = table.cell(row_index, col_index)
            cell.text = value
            cell.fill.solid()
            if row_index == 0:
                cell.fill.fore_color.rgb = BLUE
            else:
                cell.fill.fore_color.rgb = LIGHT if row_index % 2 == 0 else WHITE
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.08)
            cell.margin_top = Inches(0.01)
            cell.margin_bottom = Inches(0.01)
            for paragraph in cell.text_frame.paragraphs:
                paragraph.alignment = aligns[col_index] if aligns else PP_ALIGN.LEFT
                for run in paragraph.runs:
                    run.font.name = FONT
                    run.font.size = Pt(font_size)
                    run.font.bold = row_index == 0
                    run.font.color.rgb = WHITE if row_index == 0 else NAVY
    return table


def add_image(
    slide: object,
    path: Path,
    x: float,
    y: float,
    w: float,
    h: float,
) -> None:
    """Place an image inside a box, preserving its aspect ratio."""
    with Image.open(path) as image:
        image_width, image_height = image.size
    scale = min(w / image_width, h / image_height)
    display_width = image_width * scale
    display_height = image_height * scale
    slide.shapes.add_picture(
        str(path),
        Inches(x + (w - display_width) / 2),
        Inches(y + (h - display_height) / 2),
        width=Inches(display_width),
        height=Inches(display_height),
    )


def add_card(
    slide: object,
    x: float,
    y: float,
    w: float,
    h: float,
    value: str,
    label: str,
    accent: RGBColor = BLUE,
) -> None:
    """Add a compact metric card."""
    add_rect(slide, x, y, w, h, LIGHT, line=BORDER, rounded=True)
    add_rect(slide, x, y, 0.07, h, accent)
    add_text(slide, x + 0.22, y + 0.12, w - 0.35, 0.5, value, size=23, color=accent, bold=True)
    add_text(slide, x + 0.22, y + 0.68, w - 0.35, h - 0.75, label, size=11, color=GRAY)


def add_footer(slide: object, number: int) -> None:
    """Add the standard footer and slide number."""
    add_rect(slide, 0.65, 7.02, 12.0, 0.012, BORDER)
    add_text(slide, 0.65, 7.08, 8.0, 0.25, "Bike Sharing DOE Analysis", size=9, color=GRAY)
    add_text(
        slide,
        11.6,
        7.08,
        1.05,
        0.25,
        str(number),
        size=9,
        color=GRAY,
        align=PP_ALIGN.RIGHT,
    )


def new_slide(prs: Presentation, title: str, *, kicker: str | None = None) -> object:
    """Create a standard content slide with header rule and footer."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(slide, 0, 0, SLIDE_WIDTH, 0.13, BLUE)
    if kicker:
        add_text(slide, 0.65, 0.3, 12.0, 0.24, kicker.upper(), size=10, color=TEAL, bold=True)
        add_text(slide, 0.65, 0.58, 12.0, 0.6, title, size=27, color=NAVY, bold=True)
    else:
        add_text(slide, 0.65, 0.42, 12.0, 0.65, title, size=27, color=NAVY, bold=True)
    add_rect(slide, 0.65, 1.3, 12.0, 0.012, BORDER)
    add_footer(slide, len(prs.slides))
    return slide


def add_notes(slide: object, text: str) -> None:
    """Attach concise speaker notes to a slide."""
    slide.notes_slide.notes_text_frame.text = text


def normalize_zip(path: Path) -> None:
    """Rewrite the package with fixed timestamps so regeneration is byte-identical."""
    temporary = path.with_suffix(".pptx.tmp")
    fixed = (1980, 1, 1, 0, 0, 0)
    with ZipFile(path, "r") as source, ZipFile(temporary, "w", ZIP_DEFLATED) as target:
        for item in source.infolist():
            info = ZipInfo(item.filename, date_time=fixed)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = item.external_attr
            info.create_system = 0
            target.writestr(info, source.read(item.filename))
    temporary.replace(path)


def build() -> None:
    """Generate every slide from the validated analysis artifacts."""
    prs = Presentation()
    prs.slide_width = Inches(SLIDE_WIDTH)
    prs.slide_height = Inches(SLIDE_HEIGHT)

    properties = prs.core_properties
    properties.title = "Statistical Analysis and Demand Prediction for Bike Sharing"
    properties.subject = "A DOE-informed observational study of hourly Capital Bikeshare demand"
    properties.author = "[First Author Name], [Second Author Name]"
    properties.last_modified_by = "[First Author Name], [Second Author Name]"
    properties.category = "SBC presentation"
    properties.keywords = "bike sharing; design of experiments; ANOVA; regression; prediction"
    properties.comments = "Generated by presentation/build_slides.py"
    properties.created = datetime(2026, 1, 1)
    properties.modified = datetime(2026, 1, 1)

    # 1. Title
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(slide, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, NAVY)
    add_rect(slide, 0, 0, 0.22, SLIDE_HEIGHT, TEAL)
    add_text(
        slide,
        0.85,
        0.8,
        11.5,
        0.35,
        "SBC 2026  ·  DESIGN OF EXPERIMENTS",
        size=13,
        color=TEAL,
        bold=True,
    )
    add_text(
        slide,
        0.85,
        1.55,
        11.4,
        2.0,
        "Statistical Analysis and Demand Prediction\nfor Bike Sharing",
        size=38,
        color=WHITE,
        bold=True,
    )
    add_text(
        slide, 0.85, 3.6, 11.4, 0.5, "A DOE-informed observational study", size=21, color=BORDER
    )
    add_rect(slide, 0.85, 4.5, 3.2, 0.035, TEAL)
    add_text(
        slide,
        0.85,
        4.85,
        11.4,
        0.9,
        "[First Author Name], [Second Author Name]\n[Department and University]",
        size=15,
        color=BORDER,
    )
    add_text(
        slide,
        0.85,
        6.25,
        11.4,
        0.35,
        "17,379 hourly rentals  ·  Capital Bikeshare, Washington, D.C.  ·  2011–2012",
        size=12,
        color=GRAY,
    )
    add_notes(
        slide,
        "Introduce the study as an observational analysis with a natural factorial "
        "structure. Emphasise that the aim is description, association and short-term "
        "prediction, not causal inference.",
    )

    # 2. Objectives and flow
    slide = new_slide(prs, "Research questions and analysis flow", kicker="Overview")
    add_card(
        slide,
        0.65,
        1.55,
        5.85,
        1.75,
        "Explain",
        "Which factors are associated with hourly demand, and does the hour profile depend on working-day status?",
        TEAL,
    )
    add_card(
        slide,
        6.8,
        1.55,
        5.85,
        1.75,
        "Predict",
        "Can those factors forecast demand in a later, unseen quarter?",
        ORANGE,
    )
    stages = [
        "Descriptive",
        "Factorial ANOVA",
        "Scale + diagnostics",
        "Regression",
        "Temporal test",
    ]
    for index, stage in enumerate(stages):
        x = 0.65 + index * 2.45
        add_rect(slide, x, 3.9, 2.2, 0.85, LIGHT, line=BORDER, rounded=True)
        add_text(
            slide,
            x + 0.1,
            4.12,
            2.0,
            0.45,
            stage,
            size=12,
            color=NAVY,
            bold=True,
            align=PP_ALIGN.CENTER,
        )
        if index < len(stages) - 1:
            add_text(
                slide,
                x + 2.22,
                4.1,
                0.25,
                0.4,
                "›",
                size=22,
                color=TEAL,
                bold=True,
                align=PP_ALIGN.CENTER,
            )
    add_bullets(
        slide,
        0.65,
        5.15,
        12.0,
        1.4,
        [
            "One prespecified interaction: hour × working-day status.",
            "One regression model, one chronological split, three test metrics.",
        ],
        size=15,
    )
    add_notes(
        slide,
        "Walk through the five-stage flow. The scope is deliberately compact: one model, one split and three metrics.",
    )

    # 3. Dataset and design
    slide = new_slide(prs, "Dataset and study design", kicker="Data")
    add_table(
        slide,
        0.65,
        1.6,
        5.6,
        3.5,
        [
            ["Item", "Value"],
            ["Observed hours", "17,379"],
            ["Calendar", "731 days, 2011–2012"],
            ["Response cnt", "1–977 rentals per hour"],
            ["Absent timestamps", "165 (not imputed)"],
            ["Response mean", "189.46 rentals"],
        ],
        widths=[2.0, 1.4],
        font_size=13,
    )
    add_bullets(
        slide,
        6.65,
        1.65,
        6.0,
        4.7,
        [
            "Observational, unrandomised, unblocked and naturally factorial.",
            "Records are sequential in time; independence is not assumed.",
            "cnt = casual + registered; both components are excluded as predictors.",
            "atemp is excluded: correlation with temp is 0.988.",
            "No treatment was assigned, so results are associations.",
        ],
        size=15,
    )
    add_notes(
        slide,
        "State the unit of observation. Explain why casual and registered would leak the response and why absent hours were left unimputed.",
    )

    # 4. Factors and hypotheses
    slide = new_slide(prs, "Factors, covariates and hypotheses", kicker="Design")
    add_table(
        slide,
        0.65,
        1.6,
        6.4,
        3.7,
        [
            ["Factor", "Levels", "Role"],
            ["hr", "24", "Primary factor"],
            ["workingday", "2", "Primary factor"],
            ["weathersit", "3 pooled", "Primary factor"],
            ["season", "4", "Primary factor"],
            ["yr", "2", "Adjustment"],
        ],
        widths=[1.4, 1.0, 1.6],
        font_size=13,
    )
    add_bullets(
        slide,
        7.35,
        1.65,
        5.3,
        4.6,
        [
            "Hour is expected to dominate the daily demand profile.",
            "Working-day status should change the shape of that profile.",
            "Adverse weather should be associated with lower demand.",
            "Raw weather level 4 has only three hours; levels 3 and 4 are pooled.",
            "temp, hum, windspeed and yr enter as adjustments.",
        ],
        size=15,
    )
    add_notes(
        slide,
        "Explain pooling: severe weather has three observations, so combining it with light precipitation avoids unreliable separate contrasts. The raw variable remains in the data audit.",
    )

    # 5. Descriptive statistics
    slide = new_slide(prs, "Descriptive analysis of cnt", kicker="Results")
    add_table(
        slide,
        0.65,
        1.6,
        5.0,
        4.65,
        [
            ["Statistic", "Value"],
            ["Mean", "189.46"],
            ["Median", "142"],
            ["Standard deviation", "181.39"],
            ["Q1 – Q3", "40 – 281"],
            ["Minimum – maximum", "1 – 977"],
            ["Skewness", "1.277"],
        ],
        widths=[1.5, 1.0],
        font_size=13,
    )
    add_image(slide, FIGURES / "response_distributions.png", 5.95, 1.62, 6.7, 4.65)
    add_text(
        slide,
        6.1,
        6.4,
        6.4,
        0.4,
        "The mean exceeds the median: the raw distribution is right-skewed.",
        size=12,
        color=GRAY,
    )
    add_notes(
        slide,
        "Highlight the gap between mean and median. The histogram shows the long right tail; the log panel anticipates the scale comparison.",
    )

    # 6. Factor means
    slide = new_slide(prs, "Unadjusted means by factor", kicker="Results")
    add_table(
        slide,
        0.65,
        1.6,
        5.3,
        4.4,
        [
            ["Pooled weather", "Mean", "Season", "Mean"],
            ["Clear/partly cloudy", "204.87", "Spring", "111.11"],
            ["Mist/cloudy", "175.17", "Summer", "208.34"],
            ["Precipitation/adverse", "111.50", "Fall", "236.02"],
            ["", "", "Winter", "198.87"],
        ],
        widths=[1.6, 0.8, 1.0, 0.8],
        font_size=11,
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.LEFT, PP_ALIGN.RIGHT],
    )
    add_image(slide, FIGURES / "factor_boxplots.png", 6.2, 1.6, 6.45, 4.5)
    add_text(
        slide,
        0.7,
        6.25,
        11.8,
        0.55,
        "These are marginal means; imbalances across hour, season and weather can explain part of each difference.",
        size=12,
        color=GRAY,
    )
    add_notes(
        slide,
        "Use this slide to distinguish descriptive margins from adjusted model terms. The adverse category pools 1,419 light-precipitation hours and three severe-weather hours.",
    )

    # 7. Main effects
    slide = new_slide(prs, "Main effects of the four factors", kicker="Factorial view")
    add_image(slide, FIGURES / "main_effects.png", 0.75, 1.55, 11.8, 4.95)
    add_text(
        slide,
        0.75,
        6.55,
        11.8,
        0.35,
        "Hour and season are the clearest margins; the working-day margin alone is small.",
        size=12,
        color=GRAY,
    )
    add_notes(
        slide,
        "Point to the hour and season panels. The small working-day margin is misleading because it averages over the hour interaction shown next.",
    )

    # 8. Interaction
    slide = new_slide(prs, "The hour × working-day interaction", kicker="Prespecified hypothesis")
    add_image(slide, FIGURES / "workingday_hr_interaction.png", 0.7, 1.55, 8.2, 4.85)
    add_bullets(
        slide,
        9.15,
        1.8,
        3.5,
        4.5,
        [
            "Working days peak near 08:00 and 17:00–18:00.",
            "Non-working days show a broader midday peak.",
            "Partial eta-squared: 0.589.",
            "Working-day status must be read jointly with hour.",
        ],
        size=14,
    )
    add_notes(
        slide,
        "This is the central structural finding. The commuting peaks are visible only when the two factors are examined together.",
    )

    # 9. Factorial ANOVA
    slide = new_slide(prs, "Factorial ANOVA on log(1 + cnt)", kicker="Inference")
    add_table(
        slide,
        0.65,
        1.55,
        9.4,
        5.0,
        [
            ["Term", "df", "F", "Partial η²"],
            ["Hour", "23", "5416.44", "0.878"],
            ["Working day", "1", "12.27", "0.001"],
            ["Weather condition", "2", "1180.12", "0.120"],
            ["Season", "3", "1163.90", "0.168"],
            ["Year", "1", "6204.50", "0.264"],
            ["Hour × working day", "23", "1079.55", "0.589"],
            ["Temperature", "1", "3237.28", "0.157"],
            ["Humidity", "1", "100.45", "0.006"],
            ["Wind speed", "1", "113.13", "0.006"],
        ],
        widths=[2.4, 0.6, 1.1, 1.0],
        font_size=11,
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.CENTER, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT],
    )
    add_card(slide, 10.3, 1.6, 2.35, 1.45, "0.878", "Hour effect", TEAL)
    add_card(slide, 10.3, 3.2, 2.35, 1.45, "0.589", "Interaction", BLUE)
    add_card(slide, 10.3, 4.8, 2.35, 1.45, "0.120", "Weather", ORANGE)
    add_notes(
        slide,
        "All p-values are below 0.001 given the sample size, so focus on partial eta-squared and the chronological test. Type-II sums of squares are used because the design is unbalanced.",
    )

    # 10. Tukey HSD
    slide = new_slide(prs, "Post-hoc comparison of weather conditions", kicker="Tukey HSD")
    add_table(
        slide,
        0.65,
        1.65,
        8.5,
        2.4,
        [
            ["Contrast (log scale)", "Difference", "95% simultaneous CI", "Adj. p"],
            ["Clear – mist", "0.142", "0.084 to 0.199", "< 0.001"],
            ["Clear – adverse", "0.691", "0.599 to 0.784", "< 0.001"],
            ["Mist – adverse", "0.550", "0.450 to 0.650", "< 0.001"],
        ],
        widths=[2.0, 0.9, 1.7, 0.8],
        font_size=12,
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.CENTER, PP_ALIGN.CENTER],
    )
    add_card(slide, 9.45, 1.65, 3.2, 2.4, "3 / 3", "Adjusted contrasts significant", TEAL)
    add_bullets(
        slide,
        0.65,
        4.45,
        12.0,
        1.9,
        [
            "Tukey HSD controls the family-wise error rate across the three pairs.",
            "The ordering matches the unadjusted means.",
            "The adverse category is heterogeneous: it pools two rare raw levels.",
        ],
        size=15,
    )
    add_notes(
        slide,
        "The omnibus weather effect is significant, so post-hoc contrasts are justified. The table reports first group minus second group; positive values mean the first condition has higher log demand.",
    )

    # 11. Response scale
    slide = new_slide(prs, "Choosing the response scale", kicker="Assumptions")
    add_image(slide, DIAGNOSTICS / "scale_residual_diagnostics.png", 0.65, 1.55, 7.4, 5.0)
    add_table(
        slide,
        8.3,
        1.75,
        4.35,
        2.3,
        [
            ["Response", "Adj. R²", "Shapiro W", "BP LM"],
            ["cnt", "0.812", "0.972", "4282.8"],
            ["log(1 + cnt)", "0.927", "0.949", "1672.5"],
        ],
        widths=[1.5, 0.8, 0.9, 0.9],
        font_size=10,
        aligns=[PP_ALIGN.LEFT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT, PP_ALIGN.RIGHT],
    )
    add_bullets(
        slide,
        8.35,
        4.4,
        4.2,
        2.1,
        [
            "The log scale fits better and reduces heteroscedasticity.",
            "Shapiro–Wilk rejects normality on both scales.",
            "The choice is a variance-and-fit compromise.",
        ],
        size=12,
    )
    add_notes(
        slide,
        "Do not claim that the log scale fixes normality. The residual-versus-fitted and Q–Q panels support a variance-based choice, not a normality pass.",
    )

    # 12. Residual dependence
    slide = new_slide(prs, "Residual diagnostics and temporal dependence", kicker="Assumptions")
    add_image(slide, DIAGNOSTICS / "residual_acf.png", 0.65, 1.55, 8.4, 4.7)
    add_bullets(
        slide,
        9.3,
        1.8,
        3.4,
        4.4,
        [
            "ACF lag 1: 0.612.",
            "Lag 24: 0.243.",
            "Lag 168: 0.200.",
            "Dependence remains after the included factors.",
            "ANOVA p-values are read descriptively.",
        ],
        size=14,
    )
    add_notes(
        slide,
        "Lags are observed hours, not continuous calendar hours, because 165 timestamps are absent. The residual ACF motivates reliance on the chronological test set.",
    )

    # 13. Regression model
    slide = new_slide(prs, "One prespecified regression model", kicker="Model")
    add_rect(slide, 0.65, 1.6, 12.0, 1.25, NAVY, rounded=True)
    add_text(
        slide,
        0.95,
        1.84,
        11.4,
        0.8,
        "log1p(cnt) ~ C(hr) * C(workingday) + C(weather_group) + C(season)\n             + temp + hum + windspeed + C(yr)",
        size=16,
        color=WHITE,
        font=MONO,
    )
    add_card(slide, 0.65, 3.25, 2.85, 1.55, "57", "Parameters", BLUE)
    add_card(slide, 3.7, 3.25, 2.85, 1.55, "0.927", "Adjusted R²", TEAL)
    add_card(slide, 6.75, 3.25, 2.85, 1.55, "15914.2", "AIC", ORANGE)
    add_card(slide, 9.8, 3.25, 2.85, 1.55, "16356.7", "BIC", GRAY)
    add_bullets(
        slide,
        0.7,
        5.25,
        11.8,
        1.3,
        [
            "The interaction includes both component main effects (hierarchy principle).",
            "Duan's smearing correction returns log predictions to count scale.",
        ],
        size=14,
    )
    add_notes(
        slide,
        "Mention that no model search was performed. The formula is the single model used for both explanation and prediction.",
    )

    # 14. Temporal validation
    slide = new_slide(prs, "Strictly chronological train/test split", kicker="Prediction")
    add_text(slide, 0.7, 1.6, 3.0, 0.35, "Training", size=13, color=BLUE, bold=True)
    add_text(slide, 9.9, 1.6, 2.6, 0.35, "Test", size=13, color=ORANGE, bold=True)
    add_rect(slide, 0.7, 2.0, 8.6, 0.75, BLUE, rounded=True)
    add_rect(slide, 9.45, 2.0, 3.15, 0.75, ORANGE, rounded=True)
    add_text(
        slide,
        0.95,
        2.2,
        8.1,
        0.4,
        "15,211 hours · through 30 Sep 2012",
        size=14,
        color=WHITE,
        bold=True,
    )
    add_text(slide, 9.65, 2.2, 2.75, 0.4, "2,168 hours · Q4 2012", size=13, color=WHITE, bold=True)
    add_card(slide, 0.7, 3.4, 3.75, 1.75, "45.27", "MAE (rentals)", BLUE)
    add_card(slide, 4.8, 3.4, 3.75, 1.75, "72.97", "RMSE (rentals)", TEAL)
    add_card(slide, 8.9, 3.4, 3.7, 1.75, "0.869", "Out-of-sample R²", ORANGE)
    add_text(
        slide,
        0.7,
        5.55,
        11.9,
        0.9,
        "Both years remain in training so that yr is estimable; random splitting would mix future and past observations.",
        size=14,
        color=GRAY,
    )
    add_notes(
        slide,
        "Explain the split logic and the back-transformation. Report only MAE, RMSE and out-of-sample R² on the count scale.",
    )

    # 15. Predictions
    slide = new_slide(prs, "Predictions on the unseen quarter", kicker="Prediction")
    add_image(slide, FIGURES / "test_predictions.png", 0.7, 1.55, 11.9, 4.9)
    add_text(
        slide,
        0.75,
        6.5,
        11.8,
        0.4,
        "The model tracks the daily rhythm and seasonal decline, but large-hour errors remain.",
        size=12,
        color=GRAY,
    )
    add_notes(
        slide,
        "Use the scatter panel to discuss heteroscedasticity at high demand and the daily panel to show short-term extrapolation within the observed system.",
    )

    # 16. Conclusions
    slide = new_slide(prs, "Conclusions and limitations", kicker="Takeaways")
    add_bullets(
        slide,
        0.65,
        1.65,
        7.3,
        4.9,
        [
            "Hour is the dominant factor, with partial eta-squared 0.878.",
            "The hour × working-day interaction is the key structure (0.589).",
            "Weather, season, temperature and year provide useful adjustment.",
            "The log-response model reaches adjusted R² 0.927.",
            "On the Q4 2012 test set: MAE 45.27, RMSE 72.97, R² 0.869.",
            "Associations and predictions do not establish causality.",
        ],
        size=15,
    )
    add_card(
        slide,
        8.35,
        1.65,
        4.3,
        2.2,
        "Caveat",
        "No randomisation; residual autocorrelation remains.",
        ORANGE,
    )
    add_card(
        slide,
        8.35,
        4.05,
        4.3,
        2.2,
        "Caveat",
        "Three severe-weather hours are pooled with light precipitation.",
        TEAL,
    )
    add_notes(
        slide,
        "Close by separating descriptive and predictive value from causal claims. Mention that mixed-effects, autoregressive and count-distribution models were not investigated.",
    )

    # 17. Closing
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_rect(slide, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, NAVY)
    add_rect(slide, 0, 0, 0.22, SLIDE_HEIGHT, TEAL)
    add_text(slide, 0.85, 2.5, 11.5, 1.0, "Questions", size=44, color=WHITE, bold=True)
    add_rect(slide, 0.85, 3.8, 3.2, 0.035, TEAL)
    add_text(
        slide,
        0.85,
        4.2,
        11.4,
        1.1,
        "[First Author Name] · [author emails]\n[Department and University]",
        size=15,
        color=BORDER,
    )
    add_notes(
        slide,
        "Invite questions about the factorial interpretation, the pooling decision and the chronological validation.",
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUTPUT)
    normalize_zip(OUTPUT)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {len(prs.slides)} slides.")


if __name__ == "__main__":
    build()
