"""
Name:       Jesse James
CS230:      Section 3
Data:       LEGO Stores in the USA and Canada
URL:        

Description:
This program explores LEGO store locations across the United States and Canada.
Users can filter stores by state and country, view stores on an interactive map,
compare store counts by state with a bar chart, and see a country breakdown
with a pie chart. The app uses a sidebar for navigation and interactive widgets
to let users customize what they see.

References:
    - Streamlit docs: https://docs.streamlit.io
    - PyDeck docs:    https://deckgl.readthedocs.io
    - Plotly docs:    https://plotly.com/python/
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# Page config
st.set_page_config(page_title="LEGO Store Explorer", page_icon="🧱", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("LegoUSACanada.csv")
    # [COLUMNS]
    df["Location"] = df["City"] + ", " + df["State"]
    # [COLUMNS]
    df = df.drop(columns=["Street"])
    return df
# functions
# [FUNC2P]
def filter_stores(df, states, country="All"):
    # [FILTER1] – filter by state
    result = df[df["State"].isin(states)]
    # [FILTER2] – filter by country
    if country != "All":
        result = result[result["Country"] == country]
    return result

# [FUNCRETURN2] – returns two values
def get_state_counts(df):
    # [SORT] – sort by store count
    counts = (
        df.groupby(["State", "Country"])
        .size()
        .reset_index(name="Stores")
        .sort_values("Stores", ascending=False)
    )
    # [MAXMIN] – find the state with the most stores
    busiest = counts.iloc[0]["State"] if not counts.empty else "N/A"
    return counts, busiest

# [FUNCCALL2] – called on both the Overview page and the Analysis page
def make_bar_chart(counts, top_n):
    data = counts.head(top_n)
    fig = px.bar(
        data,
        x="State",
        y="Stores",
        color="Country",
        color_discrete_map={"USA": "#D01012", "CAN": "#FFCF02"},
        title=f"Top {top_n} States by Number of LEGO Stores",
        labels={"Stores": "Number of Stores", "State": "State / Province"},
        text="Stores",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(xaxis_tickangle=-40, legend_title_text="Country")
    return fig

# Load data
df_all = load_data()
all_states = sorted(df_all["State"].unique().tolist())

# [ST3] – navigation and filters
st.sidebar.title("🧱 LEGO Store Explorer")
page = st.sidebar.radio("Go to", ["Overview", "Store Map", "State Analysis", "Find a Store"])
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total stores in dataset:** {len(df_all)}")

# PAGE 1 – OVERVIEW
if page == "Overview":
    st.title("🧱 LEGO Store Explorer")
    st.write(
        "Welcome! This app lets you explore all official LEGO store locations "
        "across the **United States** and **Canada**. Use the sidebar to navigate."
    )
    # Quick stats row
    col1, col2, col3 = st.columns(3)
    col1.write(f"**Total Stores:** {len(df_all)}")
    col2.write(f"**US Stores:** {len(df_all[df_all['Country'] == 'USA'])}")
    col3.write(f"**Canada Stores:** {len(df_all[df_all['Country'] == 'CAN'])}")
    st.markdown("---")
    # [ST2] Bar chart with slider
    top_n = st.slider("How many states to show?", min_value=5, max_value=44, value=15)

    counts_all, busiest_all = get_state_counts(df_all)   # [FUNCCALL2]
    st.plotly_chart(make_bar_chart(counts_all, top_n), use_container_width=True)  # [FUNCCALL2]
    st.markdown("---")
    # [CHART2] Pie chart of USA vs Canada
    st.subheader("USA vs Canada Breakdown")
    country_counts = df_all["Country"].value_counts().reset_index()
    country_counts.columns = ["Country", "Stores"]
    fig_pie = px.pie(
        country_counts,
        names = "Country",
        values = "Stores",
        color = "Country",
        color_discrete_map = {"USA": "#D01012", "CAN": "#FFCF02"},
        title = "Share of Stores by Country",
        hole = 0.35,
    )
    fig_pie.update_traces(textinfo="percent+label+value")
    st.plotly_chart(fig_pie, use_container_width=True)

# PAGE 2 – STORE MAP
elif page == "Store Map":
    st.title("🗺️ LEGO Store Map")
    st.write("Every LEGO store plotted on the map. Hover over a dot for details.")
    # [ST1] – dropdown to pick country
    country_choice = st.selectbox("Filter by country", ["All", "USA", "CAN"])
    df_map = filter_stores(df_all, all_states, country=country_choice)
    st.write(f"Showing **{len(df_map)}** stores.")
    # Color dots by country
    df_map = df_map.copy()
    df_map["color"] = df_map["Country"].map({
        "USA": [208, 16, 18, 200],
        "CAN": [255, 207, 2, 200],
    })
    # Simplified map using st.map
    map_data = df_map[["Latitude", "Longitude"]].rename(columns={"Latitude": "latitude", "Longitude": "longitude"})
    st.map(map_data)
    st.caption(f"Showing {len(df_map)} stores")

# PAGE 3 – STATE ANALYSIS
elif page == "State Analysis":
    st.title("📊 Stores by State")
    st.write("Use the controls below to explore store counts across states.")
    # [ST1] – multi-select for states
    chosen_states = st.multiselect(
        "Select states to include (leave empty = all)",
        options=all_states,
        default=[],
    )
    # [ST2] – slider
    top_n2 = st.slider("Number of states to show in chart", 5, 44, 20)
    states_to_use = chosen_states if chosen_states else all_states
    df_filtered = filter_stores(df_all, states_to_use)
    counts_filtered, busiest_filtered = get_state_counts(df_filtered)  # #[FUNCCALL2] – call 2
    st.plotly_chart(make_bar_chart(counts_filtered, top_n2), use_container_width=True)  # #[FUNCCALL2] – call 2b

    # [DICTMETHOD] – build a dict from the counts and use two dict methods
    state_dict = dict(zip(counts_filtered["State"], counts_filtered["Stores"]))
    st.write(f"**States shown:** {len(state_dict.keys())}")   # .keys()
    st.write(f"**Total stores:** {sum(state_dict.values())}")  # .values()

    # [ITERLOOP] – loop through the dict to list top 3 states
    top3 = []
    for state, count in list(state_dict.items())[:3]:          # .items()
        top3.append(f"{state} ({count} stores)")
    st.write("**Top 3 states:** " + " · ".join(top3))
    st.markdown("---")
    st.subheader("Full Ranked Table")
    st.table(counts_filtered.reset_index(drop=True))

# PAGE 4 – FIND A STORE
elif page == "Find a Store":
    st.title("🔍 Find a Store")
    st.write("Pick a state and country to see matching stores.")
    col_a, col_b = st.columns(2)
    # [ST1] – dropdown for state
    with col_a:
        state_choice = st.selectbox("State / Province", ["(All)"] + all_states)
    # [ST1] – dropdown for country
    with col_b:
        country_choice2 = st.selectbox("Country", ["All", "USA", "CAN"])
    states_list = all_states if state_choice == "(All)" else [state_choice]
    df_results = filter_stores(df_all, states_list, country=country_choice2)
    # [SORT] – sort results alphabetically by city then store name
    df_results = df_results.sort_values(["City", "Store Name"]).reset_index(drop=True)
    st.write(f"**{len(df_results)} store(s) found**")
    if df_results.empty:
        st.warning("No stores match. Try different filters.")
    else:
        st.table(df_results[["Store Name", "Location", "Zip", "Country", "Full Address"]])
# Footer
st.sidebar.markdown("---")
st.sidebar.caption("CS230 Final Project | LEGO Store Data")
