"""Smart Food Analysis dashboard (Streamlit): recognise a meal, grade how healthy it is, track the day."""
import csv
import os
import threading
from datetime import date, datetime
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st
from PIL import Image

from food_analyzer import LOW_CONFIDENCE, analyze_food, classifier, device_name
from nutrition import (DAILY_VALUES, GRADE_COLORS, GRADE_MEANING, NUTRIENT_NAMES, all_foods,
                       healthier_swaps)

HISTORY_FILE = Path(__file__).resolve().parent / "meal_history.csv"
HISTORY_FIELDS = ["date", "time", "label", "name", "grams", "grade", "kcal", "protein_g", "carbs_g",
                  "fat_g", "sat_fat_g", "sugars_g", "fiber_g", "sodium_mg"]
LIMIT_NUTRIENTS = {"sat_fat_g", "sugars_g", "sodium_mg"}

st.set_page_config(page_title="Smart Food Analysis", page_icon="🥗", layout="wide")
st.markdown("""
<style>
  .block-container {max-width: 1250px; padding-top: 1.6rem;}
  .hero {padding: 1.2rem 1.5rem; border-radius: 16px; color: #fff;
         background: linear-gradient(120deg, #1f8a5b, #48b37f);}
  .hero h1 {margin: 0; font-size: 1.9rem;} .hero p {margin: .25rem 0 0; opacity: .92;}
  .grade {display: flex; align-items: center; gap: 1rem; padding: 1rem 1.2rem; border-radius: 16px;
          background: #fff; border: 1px solid #dfe9e2;}
  .grade .letter {width: 72px; height: 72px; border-radius: 14px; color: #fff; font-size: 2.6rem;
                  font-weight: 800; display: flex; align-items: center; justify-content: center;}
  .grade .title {font-size: 1.15rem; font-weight: 700;} .grade .sub {color: #5d6f65; font-size: .9rem;}
  .chip {display: inline-block; padding: .2rem .65rem; margin: .15rem .25rem .15rem 0; border-radius: 999px;
         font-size: .82rem; background: #eef5f0; color: #2b4d3b;}
  .chip.bad {background: #fdecea; color: #a5321f;}
  .swap {padding: .8rem 1rem; border-radius: 14px; background: #fff; border: 1px solid #dfe9e2; height: 100%;}
  .swap b {font-size: 1rem;} .mini {display: inline-block; width: 26px; height: 26px; border-radius: 7px;
         color: #fff; font-weight: 800; text-align: center; line-height: 26px; margin-right: .4rem;}
  div[data-testid="stMetric"] {background: #fff; border: 1px solid #dfe9e2; padding: .8rem 1rem; border-radius: 14px;}
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading the food recognition model…")
def load_model():
    classifier()
    return device_name()


def grade_badge(health, title, subtitle):
    return (f'<div class="grade"><div class="letter" style="background:{health.color}">{health.grade}</div>'
            f'<div><div class="title">{title}</div><div class="sub">{subtitle}</div></div></div>')


def mini_grade(grade):
    return f'<span class="mini" style="background:{GRADE_COLORS[grade]}">{grade}</span>'


def read_history():
    if not HISTORY_FILE.exists():
        return pd.DataFrame(columns=HISTORY_FIELDS)
    return pd.read_csv(HISTORY_FILE)


def add_to_history(food, grams):
    portion = food.serving(grams)
    now = datetime.now()
    row = {"date": now.date().isoformat(), "time": now.strftime("%H:%M"), "label": food.label,
           "name": food.name, "grams": grams, "grade": food.health.grade,
           **{key: round(portion[key], 1) for key in DAILY_VALUES}}
    new_file = not HISTORY_FILE.exists()
    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HISTORY_FIELDS)
        if new_file:
            writer.writeheader()
        writer.writerow(row)


def daily_value_chart(percent):
    data = pd.DataFrame([
        {"Nutrient": NUTRIENT_NAMES[key], "% of daily value": round(value, 1),
         "Kind": "Limit" if key in LIMIT_NUTRIENTS and value >= 30 else
                 ("Watch" if key in LIMIT_NUTRIENTS else "Nutrient")}
        for key, value in percent.items()
    ])
    colors = alt.Scale(domain=["Nutrient", "Watch", "Limit"], range=["#48b37f", "#f2b33d", "#e0543d"])
    bars = alt.Chart(data).mark_bar(cornerRadiusEnd=4).encode(
        x=alt.X("% of daily value:Q", scale=alt.Scale(domain=[0, max(100, data["% of daily value"].max())])),
        y=alt.Y("Nutrient:N", sort=None, title=None, axis=alt.Axis(labelOverlap=False, labelLimit=140)),
        color=alt.Color("Kind:N", scale=colors, legend=alt.Legend(orient="bottom", title=None)),
        tooltip=["Nutrient", "% of daily value"],
    )
    rule = alt.Chart(pd.DataFrame({"x": [100]})).mark_rule(strokeDash=[4, 4], color="#8a9a91").encode(x=alt.X("x:Q", title=None))
    return (bars + rule).properties(height=alt.Step(30))


# ----------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### 🥗 Smart Food Analysis")
    try:
        device = load_model()
        st.success(f"Model ready · {device}")
    except Exception as exc:  # model missing or broken install
        st.error("Food model not available. Run INSTALL_WINDOWS.bat once while online.")
        st.caption(f"{type(exc).__name__}: {exc}")
        st.stop()
    calorie_target = st.number_input("My daily calorie target (kcal)", 1200, 4000, 2000, 50)
    default_grams = st.slider("Default serving size (g)", 50, 700, 300, 25)
    st.divider()
    st.caption("Recognises **101 dishes** (Food-101). Nutrition: USDA FoodData Central. "
               "Health grade: Nutri-Score method. General information, not medical advice.")
    if st.button("Quit app", icon=":material/power_settings_new:", width="stretch"):
        st.info("Smart Food Analysis has stopped. You can close this tab.")
        threading.Timer(0.8, lambda: os._exit(0)).start()
        st.stop()

st.markdown('<div class="hero"><h1>Smart Food Analysis</h1>'
            '<p>Snap your meal, see how healthy it is, and find better choices.</p></div>',
            unsafe_allow_html=True)
st.write("")
tab_analyze, tab_day, tab_explore = st.tabs(["📷 Analyze meal", "📅 My day", "🔎 Food explorer"])

# ----------------------------------------------------------------- analyze
with tab_analyze:
    source = st.segmented_control("Photo source", ["Upload", "Camera"], default="Upload",
                                  label_visibility="collapsed")
    if source == "Camera":
        photo = st.camera_input("Take a photo of your meal")
    else:
        photo = st.file_uploader("Upload a meal photo", type=["jpg", "jpeg", "png", "webp"])

    if photo is None:
        st.write("")
        a, b, c = st.columns(3)
        a.markdown("#### 1 · Photo\nUpload a clear photo of one dish or use the camera.")
        b.markdown("#### 2 · Recognise\nThe AI suggests the 3 most likely dishes; pick the right one.")
        c.markdown("#### 3 · Health check\nGet a health grade, nutrients for your portion and healthier swaps.")
    else:
        image = Image.open(photo).convert("RGB")
        with st.spinner("Recognising the dish…"):
            analysis = analyze_food(image, default_grams)

        left, right = st.columns([5, 7], gap="large")
        with left:
            st.image(image, width="stretch")
            options = {f"{g.food.name} · {g.confidence:.0%}": g.food for g in analysis.guesses}
            choice = st.radio("Which dish is it?", list(options), index=0)
            food = options[choice]
            grams = st.slider("Serving size (grams)", 50, 700, analysis.grams, 25)
            if analysis.is_uncertain:
                st.warning(
                    f"The model is not sure ({analysis.best.confidence:.0%}). It only knows 101 dishes, so a "
                    "photo of something else (fruit, vegetables, home dishes outside the list) can be "
                    "recognised wrongly. Check the guesses above.", icon="⚠️")

        with right:
            health = food.health
            st.markdown(grade_badge(health, f"{food.name}: {health.meaning}",
                                    f"Nutri-Score {health.score} · {food.category} · per 100 g"),
                        unsafe_allow_html=True)
            chips = "".join(f'<span class="chip {"bad" if r.startswith(("high", "some")) else ""}">{r}</span>'
                            for r in health.reasons())
            st.markdown(chips, unsafe_allow_html=True)

            portion = food.serving(grams)
            m1, m2 = st.columns(2)
            m1.metric(f"Calories · {100 * portion['kcal'] / calorie_target:.0f}% of your day",
                      f"{portion['kcal']:.0f} kcal")
            m2.metric("Protein", f"{portion['protein_g']:.1f} g")
            m3, m4 = st.columns(2)
            m3.metric("Carbohydrates", f"{portion['carbs_g']:.1f} g")
            m4.metric("Fat", f"{portion['fat_g']:.1f} g")
            st.markdown(f"**Daily values for {grams} g**")
            st.altair_chart(daily_value_chart(food.daily_percent(grams)), width="stretch")

            if st.button("Add to my day", icon=":material/add_circle:", type="primary"):
                add_to_history(food, grams)
                st.toast(f"Added {food.name} ({grams} g) to today")

        swaps = healthier_swaps(food)
        if swaps:
            st.markdown("#### Healthier swaps")
            for column, swap in zip(st.columns(len(swaps)), swaps):
                column.markdown(f'<div class="swap">{mini_grade(swap.health.grade)}<b>{swap.name}</b><br>'
                                f'<span style="color:#5d6f65">{swap.per_100g["kcal"]:.0f} kcal · '
                                f'{swap.per_100g["protein_g"]:.0f} g protein per 100 g</span></div>',
                                unsafe_allow_html=True)
        else:
            st.success("Great choice: nothing similar scores better.")
        with st.expander("Nutrition facts and data source"):
            facts = pd.DataFrame({"Per 100 g": food.per_100g, f"Per {grams} g": portion}).round(1)
            facts.index = [NUTRIENT_NAMES[k] + (" (mg)" if k == "sodium_mg" else " (kcal)" if k == "kcal" else " (g)")
                           for k in facts.index]
            st.dataframe(facts, width="stretch")
            st.caption(f"USDA FNDDS: {food.usda_source}. Fruit/vegetable share (estimate): "
                       f"{food.fruit_veg_pct:.0f}%.")

# ----------------------------------------------------------------- my day
with tab_day:
    history = read_history()
    today = history[history["date"] == date.today().isoformat()]
    if today.empty:
        st.info("No meals added today. Analyse a meal and press **Add to my day**.")
    else:
        totals = today[list(DAILY_VALUES)].sum()
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Calories today", f"{totals['kcal']:.0f} kcal", f"{calorie_target - totals['kcal']:.0f} left",
                  delta_color="normal" if totals["kcal"] <= calorie_target else "inverse")
        k2.metric("Meals", len(today))
        k3.metric("Protein", f"{totals['protein_g']:.0f} g")
        grade_points = today["grade"].map({"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}).mean()
        k4.metric("Average grade", "ABCDE"[round(grade_points) - 1])
        st.progress(min(totals["kcal"] / calorie_target, 1.0),
                    text=f"{totals['kcal']:.0f} of {calorie_target} kcal")
        left, right = st.columns([6, 5], gap="large")
        with left:
            st.markdown("**Nutrients vs daily values**")
            day_percent = {key: 100 * totals[key] / DAILY_VALUES[key] for key in DAILY_VALUES}
            day_percent["kcal"] = 100 * totals["kcal"] / calorie_target
            st.altair_chart(daily_value_chart(day_percent), width="stretch")
        with right:
            st.markdown("**Meals**")
            st.dataframe(today[["time", "name", "grams", "grade", "kcal"]].rename(columns=str.capitalize),
                         hide_index=True, width="stretch")
            if st.button("Clear today", icon=":material/delete:"):
                history[history["date"] != date.today().isoformat()].to_csv(HISTORY_FILE, index=False)
                st.rerun()

# ----------------------------------------------------------------- explorer
with tab_explore:
    foods = pd.DataFrame([{
        "Food": f.name, "Grade": f.health.grade, "Category": f.category.capitalize(),
        "kcal": f.per_100g["kcal"], "Protein g": f.per_100g["protein_g"], "Sugars g": f.per_100g["sugars_g"],
        "Sat. fat g": f.per_100g["sat_fat_g"], "Fibre g": f.per_100g["fiber_g"],
        "Sodium mg": f.per_100g["sodium_mg"], "Score": f.health.score,
    } for f in all_foods().values()])
    c1, c2, c3 = st.columns([3, 3, 2])
    query = c1.text_input("Search", placeholder="e.g. salad, soup, cake")
    grades = c2.multiselect("Grade", list("ABCDE"), default=list("ABCDE"))
    categories = c3.multiselect("Category", sorted(foods["Category"].unique()))
    shown = foods[foods["Grade"].isin(grades)]
    if query:
        shown = shown[shown["Food"].str.contains(query, case=False)]
    if categories:
        shown = shown[shown["Category"].isin(categories)]
    left, right = st.columns([8, 4], gap="large")
    with left:
        st.dataframe(
            shown.sort_values("Score").style.map(
                lambda g: f"background-color:{GRADE_COLORS[g]};color:white;font-weight:700", subset=["Grade"])
            .format(precision=1, subset=["Protein g", "Sugars g", "Sat. fat g", "Fibre g"])
            .format(precision=0, subset=["kcal", "Sodium mg"]),
            hide_index=True, width="stretch", height=480,
            column_config={"kcal": st.column_config.NumberColumn("kcal / 100 g", format="%d")})
    with right:
        counts = shown["Grade"].value_counts().reindex(list("ABCDE"), fill_value=0).reset_index()
        counts.columns = ["Grade", "Foods"]
        st.altair_chart(alt.Chart(counts).mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("Grade:N", sort=list("ABCDE")), y="Foods:Q",
            color=alt.Color("Grade:N", scale=alt.Scale(domain=list(GRADE_COLORS), range=list(GRADE_COLORS.values())),
                            legend=None)).properties(height=300, title="Foods per grade"), width="stretch")
        for grade, meaning in GRADE_MEANING.items():
            st.markdown(f"{mini_grade(grade)} {meaning}", unsafe_allow_html=True)
