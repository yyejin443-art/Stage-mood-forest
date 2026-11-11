import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Circle, Ellipse, Rectangle
import random

st.set_page_config(page_title="STAGE:MOOD — Forest", page_icon="🌲", layout="wide")

# Theatrical forest color palettes by time of day
TIME_PRESETS = {
    "새벽": {
        "sky": "#26364D", "horizon": "#8B7890", "ground": "#24352E",
        "foliage": ["#17382F", "#24513C", "#37664A"], "trunk": "#302820",
        "light": "#F4D8A2", "ambient": 0.22
    },
    "낮": {
        "sky": "#72A9C5", "horizon": "#D8D7B0", "ground": "#405B35",
        "foliage": ["#174B32", "#28643B", "#4B7C45"], "trunk": "#493326",
        "light": "#FFF0B5", "ambient": 0.72
    },
    "해질녘": {
        "sky": "#684B68", "horizon": "#E39A70", "ground": "#302F2D",
        "foliage": ["#183A31", "#34503A", "#69503C"], "trunk": "#2B211F",
        "light": "#FFC27B", "ambient": 0.42
    },
    "밤": {
        "sky": "#101A31", "horizon": "#26334C", "ground": "#111C1B",
        "foliage": ["#0B241F", "#123329", "#1D4031"], "trunk": "#171719",
        "light": "#B8D4F4", "ambient": 0.12
    },
}

def blend_hex(hex_color, factor):
    h = hex_color.lstrip("#")
    rgb = np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], dtype=float)
    rgb = np.clip(rgb * factor, 0, 255).astype(int)
    return "#{:02x}{:02x}{:02x}".format(*rgb)

def draw_forest(time_name, sunlight, density, fog, variation, title):
    preset = TIME_PRESETS[time_name]
    rng = random.Random(variation)
    fig, ax = plt.subplots(figsize=(13, 7.2), dpi=120)
    fig.patch.set_facecolor("#090D12")
    ax.set_facecolor(preset["sky"])

    # Sky-to-horizon gradient
    sky_rgb = np.array(plt.matplotlib.colors.to_rgb(preset["sky"]))
    horizon_rgb = np.array(plt.matplotlib.colors.to_rgb(preset["horizon"]))
    for i in range(70):
        y0 = 2.6 + i * (3.0 / 70)
        mix = i / 69
        col = sky_rgb * mix + horizon_rgb * (1 - mix)
        ax.axhspan(y0, y0 + 0.06, color=col, zorder=0)

    # Distant forest layers
    for layer, ybase in enumerate([1.45, 1.1, 0.78]):
        col = preset["foliage"][min(layer, 2)]
        xs = np.linspace(-0.5, 10.5, 24)
        for x in xs:
            height = rng.uniform(0.8, 2.0) * (0.85 if layer == 0 else 1)
            width = rng.uniform(0.45, 0.95)
            ax.add_patch(Polygon(
                [[x-width, ybase], [x, ybase+height], [x+width, ybase]],
                closed=True, facecolor=blend_hex(col, 0.78 + layer*0.12),
                edgecolor="none", alpha=0.85, zorder=1+layer
            ))

    # Forest floor
    ax.add_patch(Rectangle((0, 0), 10, 1.0, color=preset["ground"], zorder=5))
    rng_floor = random.Random(variation + 91)
    for _ in range(90):
        x = rng_floor.uniform(0, 10)
        y = rng_floor.uniform(0.05, 0.85)
        ax.plot([x, x+rng_floor.uniform(-0.12, 0.12)],
                [y, y+rng_floor.uniform(0.02, 0.12)],
                color="#9AA66A", alpha=0.15, linewidth=1, zorder=6)

    # Sun/moon glow behind the trees
    celestial_x = 5.1
    celestial_y = 3.65 if time_name != "밤" else 4.15
    glow_color = preset["light"]
    glow_alpha = max(0.12, sunlight / 130)
    for radius, alpha in [(0.95, 0.035), (0.68, 0.06), (0.42, 0.12)]:
        ax.add_patch(Circle((celestial_x, celestial_y), radius,
                            color=glow_color, alpha=alpha*glow_alpha*5,
                            linewidth=0, zorder=2))
    ax.add_patch(Circle((celestial_x, celestial_y), 0.22,
                        color=glow_color, alpha=0.85 if time_name != "밤" else 0.72,
                        linewidth=0, zorder=3))

    # Sunlight / moonlight shafts passing between trees
    beam_count = int(2 + sunlight / 12)
    beam_alpha = (sunlight / 100) * (0.07 if time_name == "밤" else 0.20)
    for i in range(beam_count):
        x = 1.0 + i * (8.0 / max(1, beam_count-1)) + rng.uniform(-0.25, 0.25)
        width_top = rng.uniform(0.04, 0.16)
        width_bottom = width_top + rng.uniform(0.35, 1.05)
        ax.add_patch(Polygon(
            [[x-width_top, 5.4], [x+width_top, 5.4],
             [x+width_bottom, 0.95], [x-width_bottom, 0.95]],
            closed=True, facecolor=glow_color, edgecolor="none",
            alpha=beam_alpha, zorder=4
        ))

    # Main foreground trees: trunks and layered canopies
    tree_positions = np.linspace(-0.05, 10.05, density)
    for idx, x in enumerate(tree_positions):
        height = rng.uniform(3.0, 5.1)
        trunk_w = rng.uniform(0.16, 0.34)
        lean = rng.uniform(-0.22, 0.22)
        trunk_color = preset["trunk"]
        # Trunk
        ax.add_patch(Polygon(
            [[x-trunk_w/2, 0.55], [x+trunk_w/2, 0.55],
             [x+lean+trunk_w*0.35, height], [x+lean-trunk_w*0.35, height]],
            closed=True, facecolor=trunk_color, edgecolor="#171916",
            linewidth=0.7, zorder=10
        ))
        # Branches
        for side in (-1, 1):
            by = rng.uniform(2.2, height-0.35)
            ax.plot([x+lean*0.4, x+side*rng.uniform(0.35, 0.75)],
                    [by, by+rng.uniform(0.25, 0.65)],
                    color=trunk_color, linewidth=rng.uniform(3, 6),
                    solid_capstyle="round", zorder=10)
        # Canopy clusters
        base_col = preset["foliage"][idx % len(preset["foliage"])]
        for j in range(8):
            cx = x + rng.uniform(-0.75, 0.75)
            cy = height + rng.uniform(-0.35, 0.95)
            rx = rng.uniform(0.38, 0.85)
            ry = rng.uniform(0.28, 0.62)
            ax.add_patch(Ellipse(
                (cx, cy), rx*2, ry*2,
                angle=rng.uniform(-25, 25),
                facecolor=blend_hex(base_col, rng.uniform(0.75, 1.22)),
                edgecolor="none", alpha=0.97, zorder=11
            ))

    # Light-catching leaves and atmospheric motes
    mote_rng = random.Random(variation + 500)
    mote_count = int(15 + fog * 2)
    for _ in range(mote_count):
        x = mote_rng.uniform(0.4, 9.6)
        y = mote_rng.uniform(0.8, 4.9)
        ax.scatter(x, y, s=mote_rng.uniform(2, 12),
                   color=glow_color, alpha=0.12 + sunlight/500,
                   linewidths=0, zorder=12)

    # Fog layers, especially visible at low light
    if fog > 0:
        for j in range(4):
            y = 0.85 + j * 0.38
            ax.add_patch(Ellipse((5, y), 12, 0.35 + fog/90,
                                 color="#DCE2D8", alpha=(fog/100)*0.10,
                                 linewidth=0, zorder=13))

    # Stage frame / title treatment
    ax.add_patch(Rectangle((0.12, 0.12), 9.76, 5.22, fill=False,
                           edgecolor="#D8CBAA", linewidth=1.1,
                           alpha=0.5, zorder=20))
    ax.text(0.42, 5.08, "STAGE:MOOD  /  FOREST SCENE",
            color="#F7F1E4", fontsize=9, weight="bold", alpha=0.88, zorder=21)
    ax.text(0.42, 4.70, title[:34], color="#FFF9ED",
            fontsize=20, weight="bold", zorder=21)
    ax.text(0.43, 0.28, f"{time_name}  ·  빛의 양 {sunlight}%  ·  숲의 밀도 {density}",
            color="#F7F1E4", fontsize=8, alpha=0.85, zorder=21)

    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.5)
    ax.axis("off")
    plt.tight_layout(pad=0)
    return fig

st.markdown("""
<style>
.stApp {background: #0b1011; color: #f4f0e7;}
[data-testid="stSidebar"] {background: #17201c;}
h1,h2,h3,p,label {color: #f4f0e7;}
</style>
""", unsafe_allow_html=True)

st.title("🌲 STAGE:MOOD")
st.caption("숲 사이로 스며드는 빛을 조율해 나만의 연극 무대를 만들어 보세요.")
st.markdown("---")

with st.sidebar:
    st.header("무대 연출 콘솔")
    scene_title = st.text_input("장면 제목", "햇살이 머무는 숲")
    time_name = st.select_slider("시간대", options=["새벽", "낮", "해질녘", "밤"], value="낮")
    sunlight = st.slider("나무 사이로 들어오는 빛", 0, 100, 65,
                         help="빛의 양을 조절하면 숲 바닥과 나뭇잎 사이의 빛줄기가 달라집니다.")
    density = st.slider("무대 위 나무의 밀도", 3, 11, 7)
    fog = st.slider("숲속 안개", 0, 100, 20)
    variation = st.slider("숲의 배치 바꾸기", 1, 100, 24)
    if st.button("🍃 새로운 숲 무대 만들기", use_container_width=True):
        st.session_state["forest_variation"] = random.randint(1, 10000)
    st.session_state.setdefault("forest_variation", variation)

active_variation = st.session_state["forest_variation"]

col_scene, col_note = st.columns([1.8, 1], gap="large")
with col_scene:
    st.subheader("무대 미리보기")
    fig = draw_forest(time_name, sunlight, density, fog, active_variation, scene_title)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

with col_note:
    st.subheader("연출 노트")
    descriptions = {
        "새벽": "밤과 아침 사이, 희미한 빛이 숲의 윤곽을 천천히 드러냅니다.",
        "낮": "나뭇잎 사이로 쏟아지는 햇살이 숲에 생명력과 깊이를 더합니다.",
        "해질녘": "낮게 기울어진 따뜻한 빛이 숲을 서정적인 장면으로 바꿉니다.",
        "밤": "달빛과 짙은 그림자가 낯설고 신비로운 숲의 분위기를 만듭니다."
    }
    st.markdown(f"### {scene_title}")
    st.write(descriptions[time_name])
    st.markdown("---")
    st.markdown("**현재 무대 설정**")
    st.write(f"- 시간대: {time_name}")
    st.write(f"- 빛의 양: {sunlight}%")
    st.write(f"- 나무 밀도: {density}")
    st.write(f"- 안개: {fog}%")
    st.markdown("---")
    st.caption("시간대와 빛의 양을 바꿔 같은 숲이 서로 다른 장면으로 보이는 과정을 탐색해 보세요.")

st.markdown("---")
st.subheader("프로젝트 소개")
st.write(
    "STAGE:MOOD — Forest는 연극 무대의 숲 세트를 상상하며 제작한 인터랙티브 무대 디자인 프로젝트입니다. "
    "사용자는 새벽·낮·해질녘·밤의 시간대와 나무 사이로 들어오는 빛의 양, 나무의 밀도, 안개를 조절해 "
    "하나의 숲 장면을 연출할 수 있습니다. 숲이라는 동일한 공간도 빛의 방향과 강도에 따라 "
    "전혀 다른 정서와 이야기를 만들어 낸다는 점을 표현합니다."
)
st.caption("Created with Python · Streamlit · Matplotlib · NumPy")
