import streamlit as st
import httpx
import pandas as pd
import os 

BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="eClipseBord", layout="wide")

st.title("eClipseBord")
st.write("Explore historical solar and lunar eclipse data")

eclipse_images = {
    "solar": "https://images-assets.nasa.gov/image/GRC-2024-C-02639/GRC-2024-C-02639~orig.jpg",
    "lunar": "https://www.nasa.gov/wp-content/uploads/2025/03/grc-2025-c-01603orig.jpg",
}

col1, col2 = st.columns([1, 3])
with col1:
    eclipse_type = st.selectbox("Choose eclipse type", ["lunar", "solar"])


st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image:
            linear-gradient(rgba(0,0,0,0.10), rgba(0,0,0,0.10)),
            url("{eclipse_images[eclipse_type]}");
        background-position: center;
        background-repeat: no-repeat;
        background-size: cover;
        background-attachment: fixed;
    }}
    h1, h2, h3, p, label, .stMarkdown {{
        color: white !important;
        text-shadow: 0px 1px 4px rgba(0,0,0,0.8);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)



response = httpx.get(f"{BACKEND_URL}/eclipses/{eclipse_type}")
data = response.json()
df = pd.DataFrame(data)
response = httpx.get(f"{BACKEND_URL}/eclipses/{eclipse_type}", timeout=30.0)

tab1, tab2, tab3 = st.tabs(["Table", "Map", "Statistics"])



with tab1:
    st.subheader(f"All {eclipse_type} eclipses")
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader(f"Eclipse locations ({eclipse_type})")
    map_response = httpx.get(f"{BACKEND_URL}/eclipses/{eclipse_type}/map")
    map_data = pd.DataFrame(map_response.json())

    def parse_coordinate(value):
        if value is None:
            return None
        value = str(value).strip()
        direction = value[-1]
        number = float(value[:-1])
        if direction in ("S", "W"):
            number = -number
        return number

    map_data["Latitude"] = map_data["Latitude"].apply(parse_coordinate)
    map_data["Longitude"] = map_data["Longitude"].apply(parse_coordinate)
    map_data = map_data.dropna(subset=["Latitude", "Longitude"])
    map_response = httpx.get(f"{BACKEND_URL}/eclipses/{eclipse_type}/map", timeout=30.0)

    color_map = {
        "T": "#c97b84",
        "A": "#d9a679",
        "P": "#7d9cad",
        "H": "#8faa8b",
    }
    map_data["color"] = map_data["Eclipse Type"].map(color_map).fillna("#999999")

    st.map(map_data, latitude="Latitude", longitude="Longitude", color="color", size=20000 , height=350)

        
    st.markdown(
    """
    <div style="font-size: 0.85rem; color: gray;">
    <span style="color:#c97b84;">●</span> Total &nbsp;
    <span style="color:#d9a679;">●</span> Annular &nbsp;
    <span style="color:#7d9cad;">●</span> Partial &nbsp;
    <span style="color:#8faa8b;">●</span> Hybrid
    </div>
    """,
    unsafe_allow_html=True,
)

with tab3:
    st.subheader(f"Eclipse type breakdown ({eclipse_type})")

    stats_response = httpx.get(f"{BACKEND_URL}/eclipses/{eclipse_type}/stats")
    stats = stats_response.json()

    def classify_type(code):
        code = str(code)
        if code.startswith("A"):
            return "Annular"
        elif code.startswith("T"):
            return "Total"
        elif code.startswith("H"):
            return "Hybrid"
        elif code.startswith("P"):
            return "Partial"
        elif code.startswith("N"):
            return "Penumbral"
        else:
            return code

    named_stats = {}
    for code, count in stats.items():
        name = classify_type(code)
        named_stats[name] = named_stats.get(name, 0) + count

    total_eclipses = sum(named_stats.values())
    most_common_type = max(named_stats, key=named_stats.get)
    most_common_count = named_stats[most_common_type]
    most_common_pct = round((most_common_count / total_eclipses) * 100, 1)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total eclipses recorded", f"{total_eclipses:,}")
    col2.metric("Most common type", most_common_type)
    col3.metric("Share of total", f"{most_common_pct}%")


    stats_response = httpx.get(f"{BACKEND_URL}/eclipses/{eclipse_type}/stats", timeout=30.0)

    st.write(
        f"Out of {total_eclipses:,} {eclipse_type} eclipses in this dataset, "
        f"**{most_common_type}** eclipses are the most frequent, making up "
        f"{most_common_pct}% of all recorded events."
    )

    chart_df = pd.DataFrame({
        "Eclipse Type": list(named_stats.keys()),
        "Count": list(named_stats.values()),
    }).sort_values("Count", ascending=False)

    st.bar_chart(chart_df.set_index("Eclipse Type"))

    with st.expander("What do these eclipse types mean?"):
        st.markdown("""
            - **Total** — the Moon/Sun is completely covered (includes catalog subtypes T, T+, T- 
                based on the eclipse path's position relative to the shadow's center)
            - **Partial** — only part of the Sun/Moon is covered
            - **Annular** — the Moon covers the Sun's center, leaving a bright ring (solar only)
            - **Hybrid** — shifts between total and annular along its path (solar only)
            - **Penumbral** — the Moon passes through Earth's faint outer shadow, no direct shadow 
                contact (lunar only; includes catalog subtypes N, Nb, Ne, Nx)
            """)

        