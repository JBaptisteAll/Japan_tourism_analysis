import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------
# 1. Page config
# -----------------------------------------------------------
st.set_page_config(
    page_title="Japan Travel Survey - Dashboard",
    layout="wide",
    page_icon="🇯🇵",
)

# -----------------------------------------------------------
# 2. Data loading
# -----------------------------------------------------------
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


@st.cache_data
def get_unique_sorted(series: pd.Series):
    return sorted(series.dropna().unique().tolist())


try:
    df = load_data("df_clean.csv")
except FileNotFoundError:
    st.error("❌ Could not find 'df_clean.csv'. Please place it next to app.py.")
    st.stop()

# -----------------------------------------------------------
# 3. Sidebar – global filters + navigation
# -----------------------------------------------------------
st.sidebar.title("⚙️ Filters & Navigation")

# Navigation
page = st.sidebar.radio(
    "Go to",
    [
        "Overview",
        "Respondent Profile",
        "Japan Interest",
        "Difficulties & Alternatives",
        "Raw Data",
    ],
)

# Global filters (only if columns exist)
filter_cols = {}

if "nationality" in df.columns:
    nat_list = ["All"] + get_unique_sorted(df["nationality"])
    nationality_filter = st.sidebar.selectbox("Filter by nationality", nat_list)
    filter_cols["nationality"] = nationality_filter

if "country" in df.columns:
    country_list = ["All"] + get_unique_sorted(df["country"])
    country_filter = st.sidebar.selectbox("Filter by country of residence", country_list)
    filter_cols["country"] = country_filter

if "age_group" in df.columns:
    age_list = ["All"] + get_unique_sorted(df["age_group"])
    age_filter = st.sidebar.selectbox("Filter by age group", age_list)
    filter_cols["age_group"] = age_filter

if "been_to_Japan" in df.columns:
    japan_list = ["All"] + get_unique_sorted(df["been_to_Japan"])
    japan_filter = st.sidebar.selectbox("Filter by Japan experience", japan_list)
    filter_cols["been_to_Japan"] = japan_filter


def apply_filters(df_source: pd.DataFrame, filters: dict) -> pd.DataFrame:
    df_filtered = df_source.copy()
    for col, val in filters.items():
        if val is not None and val != "All" and col in df_filtered.columns:
            df_filtered = df_filtered[df_filtered[col] == val]
    return df_filtered


df_filtered = apply_filters(df, filter_cols)

st.sidebar.markdown("---")
st.sidebar.write(f"📊 **Filtered respondents:** {len(df_filtered)}")

# -----------------------------------------------------------
# 4. Helper plotting functions
# -----------------------------------------------------------
def plot_bar_count(df_source: pd.DataFrame, col: str, title: str):
    """Simple count bar chart."""
    vc = df_source[col].value_counts(dropna=False).reset_index()
    vc.columns = [col, "count"]
    fig = px.bar(
        vc,
        x=col,
        y="count",
        title=title,
        text="count",
    )
    fig.update_layout(xaxis_title="", yaxis_title="Count", showlegend=False)
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def melt_multi_columns(df_source: pd.DataFrame, prefix: str, value_name: str) -> pd.DataFrame:
    """Melt all columns starting with prefix into one column."""
    cols = [c for c in df_source.columns if c.startswith(prefix)]
    if not cols:
        return pd.DataFrame(columns=[value_name])

    melted = df_source[cols].melt(value_name=value_name)
    melted = melted.dropna()
    melted[value_name] = melted[value_name].astype(str).str.strip()
    melted = melted[melted[value_name] != ""]
    return melted


# -----------------------------------------------------------
# 5. Pages
# -----------------------------------------------------------

# ---------------------- Page: Overview ----------------------
if page == "Overview":
    st.title("🇯🇵 Japan Travel Survey – Overview")

    col1, col2, col3, col4 = st.columns(4)

    # Total respondents
    with col1:
        st.metric("Total respondents", len(df_filtered))

    # Nationalities
    if "nationality" in df_filtered.columns:
        with col2:
            st.metric("Unique nationalities", df_filtered["nationality"].nunique())

    # Countries
    if "country" in df_filtered.columns:
        with col3:
            st.metric("Countries of residence", df_filtered["country"].nunique())

    # Been to Japan (approx)
    if "been_to_Japan" in df_filtered.columns:
        yes_mask = df_filtered["been_to_Japan"].astype(str).str.lower().str.startswith("yes")
        pct_yes = 100 * yes_mask.mean() if len(df_filtered) > 0 else 0
        with col4:
            st.metric("Already visited Japan (%)", f"{pct_yes:.1f}%")

    st.markdown("### 🌍 Respondents by country of residence")

    if "country" in df_filtered.columns:
        plot_bar_count(df_filtered, "country", "Number of respondents by country")
    else:
        st.info("Column 'country' not found in dataset.")

    st.markdown("### 🌐 Respondents by nationality")

    if "nationality" in df_filtered.columns:
        plot_bar_count(df_filtered, "nationality", "Number of respondents by nationality")
    else:
        st.info("Column 'nationality' not found in dataset.")


# ------------------ Page: Respondent Profile ------------------
elif page == "Respondent Profile":
    st.title("👤 Respondent Profile")

    # Age distribution
    st.markdown("### 🎂 Age group distribution")
    if "age_group" in df_filtered.columns:
        plot_bar_count(df_filtered, "age_group", "Respondents by age group")
    else:
        st.info("Column 'age_group' not found in dataset.")

    # Income distribution
    st.markdown("### 💰 Household income distribution")
    if "household_income_in_€" in df_filtered.columns:
        plot_bar_count(
            df_filtered,
            "household_income_in_€",
            "Respondents by household income band",
        )
    else:
        st.info("Column 'household_income_in_€' not found in dataset.")

    # Family situation
    st.markdown("### 👨‍👩‍👧 Family situation")
    if "family_situation" in df_filtered.columns:
        plot_bar_count(
            df_filtered,
            "family_situation",
            "Respondents by family situation",
        )
    else:
        st.info("Column 'family_situation' not found in dataset.")

    # Travel frequency
    st.markdown("### ✈️ Travel frequency")
    if "travel_frequency" in df_filtered.columns:
        plot_bar_count(
            df_filtered,
            "travel_frequency",
            "Respondents by travel frequency",
        )
    else:
        st.info("Column 'travel_frequency' not found in dataset.")


# ------------------ Page: Japan Interest ------------------
elif page == "Japan Interest":
    st.title("🎌 Interest in Japan")

    # Been to Japan
    st.markdown("### 🇯🇵 Have respondents already been to Japan?")
    if "been_to_Japan" in df_filtered.columns:
        plot_bar_count(
            df_filtered,
            "been_to_Japan",
            "Japan experience",
        )
    else:
        st.info("Column 'been_to_Japan' not found in dataset.")

    # Desired vacation duration in Japan
    st.markdown("### ⏱️ Desired trip duration in Japan")
    if "Japan_vac_duration" in df_filtered.columns:
        plot_bar_count(
            df_filtered,
            "Japan_vac_duration",
            "Desired length of stay in Japan",
        )
    else:
        st.info("Column 'Japan_vac_duration' not found in dataset.")

    # Interest ratings (dynamic: any column starting with 'rating_interest_')
    interest_cols = [c for c in df_filtered.columns if c.startswith("rating_interest_")]

    if interest_cols:
        st.markdown("### 🌟 Interest ratings for different aspects of Japan")
        for col in interest_cols:
            pretty_name = col.replace("rating_interest_", "").replace("_", " ").title()
            st.markdown(f"#### {pretty_name}")
            plot_bar_count(df_filtered, col, pretty_name)
    else:
        st.info("No columns starting with 'rating_interest_' found.")


# ------------- Page: Difficulties & Alternatives -------------
elif page == "Difficulties & Alternatives":
    st.title("⚠️ Difficulties & Alternative Destinations")

    # Difficulties related to Japan
    st.markdown("### 😰 Main difficulties when traveling to Japan")

    japan_diffs = melt_multi_columns(df_filtered, "Japan_most_difficulties_", "difficulty")

    if not japan_diffs.empty:
        vc = japan_diffs["difficulty"].value_counts().reset_index()
        vc.columns = ["difficulty", "count"]
        fig = px.bar(
            vc,
            x="difficulty",
            y="count",
            title="Most cited difficulties for Japan",
            text="count",
        )
        fig.update_layout(xaxis_title="", yaxis_title="Count", showlegend=False)
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No 'Japan_most_difficulties_' columns or no data available.")

    # Difficulties for alternative destinations
    st.markdown("### 🌍 Difficulties for alternative destinations")

    alt_diffs = melt_multi_columns(df_filtered, "alt_dest_most_difficulties_", "difficulty")

    if not alt_diffs.empty:
        vc_alt = alt_diffs["difficulty"].value_counts().reset_index()
        vc_alt.columns = ["difficulty", "count"]
        fig_alt = px.bar(
            vc_alt,
            x="difficulty",
            y="count",
            title="Most cited difficulties for alternative destinations",
            text="count",
        )
        fig_alt.update_layout(xaxis_title="", yaxis_title="Count", showlegend=False)
        fig_alt.update_traces(textposition="outside")
        st.plotly_chart(fig_alt, use_container_width=True)
    else:
        st.info("No 'alt_dest_most_difficulties_' columns or no data available.")

    # What would make Japan more attractive? (if column exists)
    st.markdown("### 💡 Suggestions to make Japan more attractive")

    if "recomendation_to_improve_attractiveness" in df_filtered.columns:
        comments = (
            df_filtered["recomendation_to_improve_attractiveness"]
            .dropna()
            .head(20)
            .reset_index(drop=True)
        )
        st.write(comments)
        st.caption("Showing up to 20 sample comments.")
    else:
        st.info("Column 'recomendation_to_improve_attractiveness' not found.")


# ---------------------- Page: Raw Data ----------------------
elif page == "Raw Data":
    st.title("📄 Raw Data")

    st.markdown("### 📊 Filtered dataset preview")
    st.dataframe(df_filtered)

    # Download button
    csv_bytes = df_filtered.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="⬇️ Download filtered data as CSV",
        data=csv_bytes,
        file_name="df_clean_filtered.csv",
        mime="text/csv",
    )

    st.markdown("### 📋 Column list")
    st.write(list(df_filtered.columns))