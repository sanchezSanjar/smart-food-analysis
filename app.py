import streamlit as st
from PIL import Image
from food_analyzer import analyze_food

st.set_page_config(page_title="Smart Food Analysis", page_icon="🥗", layout="wide")

st.markdown("""
<style>
    .block-container {max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem;}
    .hero {padding: 1.5rem 1.7rem; border-radius: 18px; background: linear-gradient(120deg,#eaf7ee,#f7fbf8); border: 1px solid #d5eadb;}
    .hero h1 {color:#174d32; margin:0 0 .4rem 0;}
    .hero p {color:#416b53; margin:0;}
    div[data-testid="stMetric"] {background:#f6faf7; border:1px solid #e0eee4; padding:1rem; border-radius:14px;}
    .small-note {color:#66756b; font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>Smart Food Analysis</h1>
  <p>Food image recognition and an easy-to-read nutrition estimate.</p>
</div>
""", unsafe_allow_html=True)
st.write("")

with st.sidebar:
    st.header("About this demo")
    st.write("Upload a meal photo to identify a likely food category and view an illustrative nutrition estimate.")
    st.caption("Nutrition values are approximate examples, not medical advice.")
    st.divider()
    st.write("Designed with readable labels and a simple workflow.")

uploaded = st.file_uploader("Upload a meal photo", type=["jpg", "jpeg", "png", "webp"])
if uploaded:
    image = Image.open(uploaded).convert("RGB")
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.subheader("Your meal")
        st.image(image, use_container_width=True)
        serving = st.slider("Estimated serving size (grams)", min_value=50, max_value=700, value=250, step=25)
    with right:
        st.subheader("Analysis")
        with st.spinner("Analyzing image… first run may download the model."):
            try:
                result = analyze_food(image, serving)
                st.metric("Likely food category", result["label"].replace("_", " ").title())
                st.caption(f"Model confidence: {result['confidence']:.0%}")
                st.write("#### Estimated nutrition")
                c1, c2 = st.columns(2)
                c1.metric("Calories", f"{result['nutrition']['calories']} kcal")
                c2.metric("Protein", f"{result['nutrition']['protein_g']} g")
                c3, c4 = st.columns(2)
                c3.metric("Carbohydrates", f"{result['nutrition']['carbs_g']} g")
                c4.metric("Fat", f"{result['nutrition']['fat_g']} g")
                st.info(result["note"])
            except Exception as exc:
                st.error("The analysis could not be completed. Check your internet connection and try again.")
                st.caption(f"Technical detail: {type(exc).__name__}: {exc}")
else:
    st.write("")
    st.subheader("How it works")
    a, b, c = st.columns(3)
    a.markdown("### 1. Upload\nChoose a clear photo of a meal.")
    b.markdown("### 2. Recognize\nA pretrained image classifier suggests a food category.")
    c.markdown("### 3. Review\nSee an approximate nutrition profile for the selected serving.")
    st.caption("This is a prototype. It does not reliably identify every ingredient, measure portion size from pixels, or provide clinical nutrition guidance.")
