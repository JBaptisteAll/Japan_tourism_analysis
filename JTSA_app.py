import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# -----------------------------------------------------------
# 1. Page config
# -----------------------------------------------------------
st.set_page_config(
    page_title="Japan Travel Survey Analysis",
    layout="wide",
    page_icon="🇯🇵",
)

# -----------------------------------------------------------
# 2. Axis labels (pretty names)
# -----------------------------------------------------------
AXIS_LABELS = {
    "age_group": "Age Group",
    "household_income_in_€": "Household Income (€)",
    "travel_frequency": "Travel Frequency",
    "been_to_Japan": "Japan Experience",
    "Japan_vac_duration": "Desired Trip Duration in Japan",
    "Japan_budget_per_week": "Preferred Budget per Week (Japan)",
    "alt_dest_budget_per_week": "Preferred Budget per Week (Alternative Destination)",
    "Japan_prefered_accomodation": "Preferred Accommodation (Japan)",
    "alt_dest_prefered_accomodation": "Preferred Accommodation (Alternative Destination)",
    "alternative_destination": "Alternative Destination",
    "most_influencial_reason_to_choose_dest": "Main Reason to Choose Destination",
    "prefecture": "Prefecture",
    "difficulty": "Difficulty",
    "theme": "Theme",
}


def get_axis_label(col: str) -> str:
    """Return a human-friendly axis label for a given column name."""
    if col is None:
        return ""
    return AXIS_LABELS.get(col, col.replace("_", " ").title())


# -----------------------------------------------------------
# 3. Data loading & preparation
# -----------------------------------------------------------

@st.cache_data
def load_data(path: str = "df_clean.csv") -> pd.DataFrame:
    df = pd.read_csv(path)

    # -------------------------------------------------------
    # 1) Map Likert scale to numeric for interest columns
    # -------------------------------------------------------
    interest_cols = [
        "rating_interest_culture_and_history",
        "rating_interest_food",
        "rating_interest_nature_hiking",
        "rating_interest_shopping_and_techno",
        "rating_interest_events_and_festivals",
        "rating_interest_wellness",
        "rating_interest_theme_park",
    ]

    likert_mapping = {
        "Not important at all": 1,
        "Slightly important": 2,
        "Moderately important": 3,
        "Very important": 4,
        "Essential": 5,
    }

    for col in interest_cols:
        if col in df.columns:
            df[col] = df[col].replace(likert_mapping)
            df[col] = df[col].replace(["0", 0], np.nan)
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # -------------------------------------------------------
    # 2) Compute interest scores
    # -------------------------------------------------------
    df["overall_interest_score"] = df[interest_cols].mean(axis=1)

    df["interest_culture_food"] = df[
        ["rating_interest_culture_and_history", "rating_interest_food"]
    ].mean(axis=1)

    df["interest_nature_wellness"] = df[
        ["rating_interest_nature_hiking", "rating_interest_wellness"]
    ].mean(axis=1)

    df["interest_urban_entertainment"] = df[
        [
            "rating_interest_shopping_and_techno",
            "rating_interest_events_and_festivals",
            "rating_interest_theme_park",
        ]
    ].mean(axis=1)

    # -------------------------------------------------------
    # 3) Category orders
    # -------------------------------------------------------
    CATEGORY_ORDERS = {
        "age_group": ["18-24", "25-34", "35-44", "45-54", "55-64", "65 and over"],
        "household_income_in_€": [
            "1500 and less",
            "1500-1999",
            "2000-2499",
            "2500-2999",
            "3000-3999",
            "4000–4999",
            "5000–5999",
            "6000–6999",
            "7000 and more",
            "Unknown",
        ],
        "travel_frequency": [
            "Several times a year",
            "Once a year",
            "Every 2–3 years",
            "Once every 5 years or more",
            "Never",
        ],
        "Japan_vac_duration": [
            "1 week",
            "2 weeks",
            "3 weeks",
            "4 weeks",
            "More than 4 weeks",
            "I don’t know yet / Not sure",
        ],
        "Japan_budget_per_week": [
            "Less than 500",
            "500-1000",
            "1000-1500",
            "1500-2500",
            "More than 2500",
            "Unknown",
        ],
        "alt_dest_budget_per_week": [
            "Less than 500",
            "500-1000",
            "1000-1500",
            "1500-2500",
            "More than 2500",
        ],
        "been_to_Japan": [
            "No, and I’m not interested",
            "No, but I would like to go",
            "Yes, once",
            "Yes, several times",
        ],
    }

    df.attrs["category_orders"] = CATEGORY_ORDERS

    return df


df = load_data()


def get_category_orders() -> dict:
    return df.attrs.get("category_orders", {})


CATEGORY_ORDERS = get_category_orders()

# -----------------------------------------------------------
# 4. Helper functions
# -----------------------------------------------------------

def apply_sidebar_filters(df_source: pd.DataFrame) -> pd.DataFrame:
    """Create sidebar filters and return the filtered dataframe."""
    st.sidebar.header("Filters")

    # Nationality
    nationalities = sorted(df_source["nationality"].dropna().unique().tolist())
    selected_nationalities = st.sidebar.multiselect(
        "Filter by nationality",
        options=nationalities,
    )

    # Country of residence
    countries = sorted(df_source["country"].dropna().unique().tolist())
    selected_countries = st.sidebar.multiselect(
        "Filter by country of residence",
        options=countries,
    )

    # Age group
    age_order = CATEGORY_ORDERS.get("age_group")
    age_values = df_source["age_group"].dropna().unique().tolist()
    if age_order:
        age_values = [a for a in age_order if a in age_values]
    else:
        age_values = sorted(age_values)

    selected_age = st.sidebar.multiselect(
        "Filter by age group",
        options=age_values,
    )

    # Income
    income_order = CATEGORY_ORDERS.get("household_income_in_€")
    income_values = df_source["household_income_in_€"].dropna().unique().tolist()
    if income_order:
        income_values = [i for i in income_order if i in income_values]
    else:
        income_values = sorted(income_values)

    selected_income = st.sidebar.multiselect(
        "Filter by household income (€)",
        options=income_values,
    )

    # Been to Japan
    been_order = CATEGORY_ORDERS.get("been_to_Japan")
    been_values = df_source["been_to_Japan"].dropna().unique().tolist()
    if been_order:
        been_values = [b for b in been_order if b in been_values]
    else:
        been_values = sorted(been_values)

    selected_been = st.sidebar.multiselect(
        "Filter by Japan experience",
        options=been_values,
    )

    # Travel frequency
    freq_order = CATEGORY_ORDERS.get("travel_frequency")
    freq_values = df_source["travel_frequency"].dropna().unique().tolist()
    if freq_order:
        freq_values = [f for f in freq_order if f in freq_values]
    else:
        freq_values = sorted(freq_values)

    selected_freq = st.sidebar.multiselect(
        "Filter by travel frequency",
        options=freq_values,
    )

    # Apply filters
    df_filtered = df_source.copy()
    if selected_nationalities:
        df_filtered = df_filtered[df_filtered["nationality"].isin(selected_nationalities)]
    if selected_countries:
        df_filtered = df_filtered[df_filtered["country"].isin(selected_countries)]
    if selected_age:
        df_filtered = df_filtered[df_filtered["age_group"].isin(selected_age)]
    if selected_income:
        df_filtered = df_filtered[df_filtered["household_income_in_€"].isin(selected_income)]
    if selected_been:
        df_filtered = df_filtered[df_filtered["been_to_Japan"].isin(selected_been)]
    if selected_freq:
        df_filtered = df_filtered[df_filtered["travel_frequency"].isin(selected_freq)]

    return df_filtered


def plot_bar_count(
    df_source: pd.DataFrame,
    col: str,
    title: str,
    order=None,
    normalize: bool = False,
    x_label: str = None,
):
    """Generic bar chart for counts or percentages."""
    if order is None:
        order = CATEGORY_ORDERS.get(col)

    vc = df_source[col].value_counts(dropna=False).rename_axis(col).reset_index(name="count")

    if normalize:
        total = vc["count"].sum()
        vc["pct"] = (vc["count"] / total * 100).round(1)
        y_col = "pct"
        y_label = "Percentage"
        text_col = "pct"
    else:
        y_col = "count"
        y_label = "Count"
        text_col = "count"

    if order:
        vc[col] = pd.Categorical(vc[col], categories=order, ordered=True)
        vc = vc.sort_values(col)

    fig = px.bar(
        vc,
        x=col,
        y=y_col,
        text=text_col,
        title=title,
    )

    # X-axis label
    if x_label is not None:
        fig.update_layout(xaxis_title=x_label)
    else:
        fig.update_layout(xaxis_title=get_axis_label(col))

    # Y-axis label
    fig.update_layout(yaxis_title=y_label)
    fig.update_traces(textposition="outside")

    st.plotly_chart(fig, use_container_width=True)


def melt_multi_columns(df_source: pd.DataFrame, prefix: str, value_name: str) -> pd.DataFrame:
    """Melt columns with a common prefix into a long format."""
    cols = [c for c in df_source.columns if c.startswith(prefix)]
    melted = df_source.melt(
        value_vars=cols,
        value_name=value_name,
        var_name="rank",
    ).dropna(subset=[value_name])
    return melted


# -----------------------------------------------------------
# 5. Sidebar navigation
# -----------------------------------------------------------
st.sidebar.title("🎌 Japan Travel Survey")

page = st.sidebar.selectbox(
    "Select a page",
    [
        "Overview",
        "Segments & Cross-Analysis",
        "Difficulties & Barriers",
        "Prefecture Wishlist",
        "Custom Funnel",
        "Text Insights",
        "Raw Data",
    ],
)

# Apply filters once for all pages
df_filtered = apply_sidebar_filters(df)

st.sidebar.markdown(f"**Number of respondents after filters:** {len(df_filtered)}")

normalize_global = st.sidebar.checkbox(
    "Show percentages instead of counts",
    value=True
)

# Ajout du lien externe dans le sidebar ou en bas de page
st.sidebar.markdown("---")
st.sidebar.markdown(
    "[📃 **Take the Survey**](https://linktr.ee/JapanAnalysis) ",
    unsafe_allow_html=True
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "[🌐 Visit My Portfolio](https://jbaptisteall.github.io/JeanBaptisteAllombert/index.html) ",
    unsafe_allow_html=True
)
st.sidebar.markdown(
    "[✉️ Contact Me](https://linktr.ee/jbcontactme) ",
    unsafe_allow_html=True
)


# -----------------------------------------------------------
# 6. Pages
# -----------------------------------------------------------

# ------------------------ Overview -------------------------
if page == "Overview":
    st.title("Japan Travel Survey — Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Number of respondents", len(df_filtered))

    with col2:
        avg_interest = df_filtered["overall_interest_score"].mean()
        st.metric("Average overall interest (1–5)", f"{avg_interest:.2f}")

    with col3:
        share_want_to_go = (
            (df_filtered["been_to_Japan"] == "No, but I would like to go").mean()
            * 100
            if len(df_filtered) > 0
            else 0
        )
        st.metric("Share who want to go (never been)", f"{share_want_to_go:.1f}%")

    st.markdown("### Demographics")

    dcol1, dcol2 = st.columns(2)
    with dcol1:
        plot_bar_count(
            df_filtered,
            "age_group",
            "Respondents by age group",
            normalize=normalize_global,
            x_label="",
        )
    with dcol2:
        plot_bar_count(
            df_filtered,
            "household_income_in_€",
            "Household income (€)",
            normalize=normalize_global,
            x_label="",
        )

    st.markdown("### Travel profile")
    tcol1, tcol2 = st.columns(2)
    with tcol1:
        plot_bar_count(
            df_filtered,
            "travel_frequency",
            "Travel frequency",
            normalize=normalize_global,
            x_label="",
        )
    with tcol2:
        plot_bar_count(
            df_filtered,
            "been_to_Japan",
            "Japan experience",
            normalize=normalize_global,
            x_label="",
        )

    st.markdown("### Interest in Japan (scores)")

    interest_cols = [
        "rating_interest_culture_and_history",
        "rating_interest_food",
        "rating_interest_nature_hiking",
        "rating_interest_shopping_and_techno",
        "rating_interest_events_and_festivals",
        "rating_interest_wellness",
        "rating_interest_theme_park",
    ]

    interest_long = (
        df_filtered[interest_cols]
        .mean()
        .reset_index()
        .rename(columns={"index": "dimension", 0: "avg_score"})
    )
    interest_long["dimension"] = interest_long["dimension"].str.replace(
        "rating_interest_", "", regex=False
    )

    fig_interest = px.bar(
        interest_long,
        x="dimension",
        y="avg_score",
        title="Average interest score by dimension",
        text="avg_score",
    )
    fig_interest.update_layout(
        xaxis_title="",
        yaxis_title="Average score (1–5)",
    )
    fig_interest.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    st.plotly_chart(fig_interest, use_container_width=True)

    st.markdown("### Trip expectations (duration & budget)")

    ecol1, ecol2 = st.columns(2)
    with ecol1:
        plot_bar_count(
            df_filtered,
            "Japan_vac_duration",
            "Desired trip duration in Japan",
            normalize=normalize_global,
            x_label="",
        )
    with ecol2:
        plot_bar_count(
            df_filtered,
            "Japan_budget_per_week",
            "Preferred budget per week (Japan)",
            normalize=normalize_global,
            x_label="",
        )

# ---------------- Segments & Cross-Analysis ----------------
elif page == "Segments & Cross-Analysis":
    st.title("Segments & Cross-Analysis")

    st.markdown(
        "Use this page to explore how distributions change by segment "
        "(age, income, Japan experience, etc.)."
    )

    all_group_cols = [
        "age_group",
        "household_income_in_€",
        "travel_frequency",
        "been_to_Japan",
        "Japan_vac_duration",
        "Japan_budget_per_week",
        "country",
        "nationality",
        "family_situation",
    ]

    group_col = st.selectbox(
        "Group by (X axis)",
        options=all_group_cols,
        index=0,
    )

    target_cols = [
        "Japan_vac_duration",
        "Japan_budget_per_week",
        "Japan_prefered_accomodation",
        "alternative_destination",
        "alt_dest_budget_per_week",
        "alt_dest_prefered_accomodation",
        "most_influencial_reason_to_choose_dest",
    ]

    target_col = st.selectbox(
        "Target distribution (stacked color)",
        options=target_cols,
        index=0,
    )



    ctab = (
        df_filtered.groupby([group_col, target_col])
        .size()
        .reset_index(name="count")
    )

    normalize = normalize_global
    if normalize:
        total_per_group = ctab.groupby(group_col)["count"].transform("sum")
        ctab["pct"] = ctab["count"] / total_per_group * 100
        y_col = "pct"
        y_label = "Percentage"
        text_col = "pct"
    else:
        y_col = "count"
        y_label = "Count"
        text_col = "count"

    group_order = CATEGORY_ORDERS.get(group_col)
    if group_order:
        ctab[group_col] = pd.Categorical(ctab[group_col], categories=group_order, ordered=True)
        ctab = ctab.sort_values(group_col)

    fig_seg = px.bar(
        ctab,
        x=group_col,
        y=y_col,
        color=target_col,
        title=f"Distribution of {target_col} by {group_col}",
        text=text_col,
    )
    if normalize:
        fig_seg.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
    else:
        fig_seg.update_traces(textposition="inside")
    fig_seg.update_layout(
        xaxis_title=get_axis_label(group_col),
        yaxis_title=y_label,
    )
    st.plotly_chart(fig_seg, use_container_width=True)

    st.markdown("---")
    st.markdown("### Average interest score by segment")

    seg_interest = (
        df_filtered.groupby(group_col)["overall_interest_score"]
        .mean()
        .reset_index()
        .rename(columns={"overall_interest_score": "avg_interest"})
    )

    if group_order:
        seg_interest[group_col] = pd.Categorical(
            seg_interest[group_col], categories=group_order, ordered=True
        )
        seg_interest = seg_interest.sort_values(group_col)

    fig_int_seg = px.bar(
        seg_interest,
        x=group_col,
        y="avg_interest",
        title=f"Average overall interest score by {group_col}",
        text="avg_interest",
    )
    fig_int_seg.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig_int_seg.update_layout(
        xaxis_title=get_axis_label(group_col),
        yaxis_title="Average interest (1–5)",
    )
    st.plotly_chart(fig_int_seg, use_container_width=True)

# ---------------- Difficulties & Barriers -------------------
elif page == "Difficulties & Barriers":
    st.title("Difficulties & Barriers")

    st.markdown("This page focuses on difficulties for Japan vs alternative destinations.")

    japan_diffs = melt_multi_columns(df_filtered, "Japan_most_difficulties_", "difficulty_japan")
    alt_diffs = melt_multi_columns(df_filtered, "alt_dest_most_difficulties_", "difficulty_alt")

    # Aggregate for Japan
    japan_counts = (
        japan_diffs["difficulty_japan"]
        .value_counts()
        .reset_index()
    )
    japan_counts.columns = ["difficulty", "count"]

    fig_japan_diff = px.bar(
        japan_counts,
        x="difficulty",
        y="count",
        title="Main difficulties when planning a trip to Japan",
        text="count",
    )
    fig_japan_diff.update_traces(textposition="outside")
    fig_japan_diff.update_layout(
        xaxis_title="Difficulty",
        yaxis_title="Count",
    )
    st.plotly_chart(fig_japan_diff, use_container_width=True)

    # Aggregate for alternative destinations
    alt_counts = (
        alt_diffs["difficulty_alt"]
        .value_counts()
        .reset_index()
    )
    alt_counts.columns = ["difficulty", "count"]

    fig_alt_diff = px.bar(
        alt_counts,
        x="difficulty",
        y="count",
        title="Main difficulties for alternative destinations",
        text="count",
    )
    fig_alt_diff.update_traces(textposition="outside")
    fig_alt_diff.update_layout(
        xaxis_title="Difficulty",
        yaxis_title="Count",
    )
    st.plotly_chart(fig_alt_diff, use_container_width=True)

    st.markdown("---")
    st.markdown("### Difficulties by segment")

    diff_group_col = st.selectbox(
        "Segment by",
        options=["been_to_Japan", "household_income_in_€", "age_group", "travel_frequency"],
        index=0,
    )

    japan_diffs_with_seg = japan_diffs.join(
        df_filtered[[diff_group_col]].reset_index(drop=True)
    )

    diff_by_seg = (
        japan_diffs_with_seg.groupby([diff_group_col, "difficulty_japan"])
        .size()
        .reset_index(name="count")
    )

    total_per_seg = diff_by_seg.groupby(diff_group_col)["count"].transform("sum")
    diff_by_seg["pct"] = diff_by_seg["count"] / total_per_seg * 100

    seg_order = CATEGORY_ORDERS.get(diff_group_col)
    if seg_order:
        diff_by_seg[diff_group_col] = pd.Categorical(
            diff_by_seg[diff_group_col], categories=seg_order, ordered=True
        )
        diff_by_seg = diff_by_seg.sort_values(diff_group_col)

    fig_diff_seg = px.bar(
        diff_by_seg,
        x=diff_group_col,
        y="pct",
        color="difficulty_japan",
        title=f"Difficulties for Japan by {diff_group_col}",
        text="pct",
    )
    fig_diff_seg.update_traces(texttemplate="%{text:.1f}%", textposition="inside")
    fig_diff_seg.update_layout(
        xaxis_title=get_axis_label(diff_group_col),
        yaxis_title="Percentage",
    )
    st.plotly_chart(fig_diff_seg, use_container_width=True)

# ------------------ Prefecture Wishlist ---------------------
elif page == "Prefecture Wishlist":
    st.title("🗾 Prefecture Wishlist")

    st.markdown(
        "Ranking of Japanese prefectures based on weighted preferences "
        "(1st choice = 5 pts, 2nd = 4 pts, ..., 5th = 1 pt)."
    )

    rank_weights = {
        "most_wanted_pref_to_visit_1": 1,
        "most_wanted_pref_to_visit_2": 1,
        "most_wanted_pref_to_visit_3": 1,
        "most_wanted_pref_to_visit_4": 1,
        "most_wanted_pref_to_visit_5": 1,
    }

    pref_scores_list = []
    for col, weight in rank_weights.items():
        if col in df_filtered.columns:
            tmp = df_filtered[[col]].rename(columns={col: "prefecture"}).dropna()
            tmp["score"] = weight
            pref_scores_list.append(tmp)

    if pref_scores_list:
        pref_scores = pd.concat(pref_scores_list, ignore_index=True)
        pref_agg = (
            pref_scores.groupby("prefecture")["score"]
            .sum()
            .reset_index()
            .sort_values("score", ascending=False)
        )

        fig_pref = px.bar(
            pref_agg,
            x="prefecture",
            y="score",
            title="Weighted preference score by prefecture",
            text="score",
        )
        fig_pref.update_traces(textposition="outside")
        fig_pref.update_layout(
            xaxis_title=get_axis_label("prefecture"),
            yaxis_title="Weighted Score",
        )
        st.plotly_chart(fig_pref, use_container_width=True)

        st.markdown("### Top 10 prefectures")
        st.dataframe(pref_agg.head(10), use_container_width=True)
    else:
        st.info("No prefecture preference data available with current filters.")

# --------------------- Custom Funnel ------------------------
elif page == "Custom Funnel":
    st.title("Custom Funnel")

    st.markdown(
        "Build a custom funnel based on any combination of categorical columns. "
        "At each step, you can either keep the most common value (Top value) "
        "or force a specific value."
    )

    funnel_cols_candidates = [
        "Japan_vac_duration",
        "Japan_budget_per_week",
        "Japan_prefered_accomodation",
        "most_influencial_reason_to_choose_dest",
        
        "alternative_destination",
        "alt_dest_budget_per_week",
        "alt_dest_prefered_accomodation",
        "alt_dest_main_reason",
        "alt_dest_transportation",

        "travel_frequency",
        "been_to_Japan",
        "household_income_in_€",
        "age_group",
        "booking_trip_channel",
        "trip_prep",
    ]

    selected_funnel_cols = st.multiselect(
        "Choose funnel steps (order matters)",
        options=funnel_cols_candidates,
        default=["booking_trip_channel", "trip_prep"],
    )

    funnel_config = {}
    for col_name in selected_funnel_cols:
        col_values = sorted(
            df_filtered[col_name].dropna().unique().tolist()
        )
        options = ["[Top value]"] + col_values
        selected_option = st.selectbox(
            f"Step for {col_name}",
            options=options,
            help="Choose '[Top value]' to automatically use the most frequent value at this step.",
        )
        funnel_config[col_name] = selected_option

    segment_by = st.selectbox(
        "Optional: segment funnel by",
        options=["None", "been_to_Japan", "age_group", "household_income_in_€"],
        index=0,
    )

    if st.button("Run funnel"):
        if len(selected_funnel_cols) == 0:
            st.warning("Please select at least one column for the funnel.")
        else:
            if segment_by == "None":
                df_step = df_filtered.copy()
                stages = []
                total_start = len(df_step)

                for col_name in selected_funnel_cols:
                    if len(df_step) == 0:
                        break

                    choice = funnel_config[col_name]
                    if choice == "[Top value]":
                        vc = df_step[col_name].value_counts(dropna=True)
                        top_value = vc.idxmax()
                    else:
                        top_value = choice

                    df_step = df_step[df_step[col_name] == top_value]
                    stages.append(
                        {
                            "step": col_name,
                            "value": top_value,
                            "remaining": len(df_step),
                            "conversion_rate": len(df_step) / total_start * 100 if total_start else 0,
                        }
                    )

                funnel_df = pd.DataFrame(stages)

                fig_funnel = px.funnel(
                    funnel_df,
                    x="remaining",
                    y="step",
                    title="Custom funnel (all respondents)",
                    text="remaining",
                )
                fig_funnel.update_layout(
                    xaxis_title="Remaining Respondents",
                    yaxis_title="Funnel Steps",
                )
                st.plotly_chart(fig_funnel, use_container_width=True)
                st.dataframe(funnel_df, use_container_width=True)

            else:
                seg_values = df_filtered[segment_by].dropna().unique().tolist()
                seg_values = sorted(seg_values)

                all_funnels = []

                for seg_val in seg_values:
                    df_seg = df_filtered[df_filtered[segment_by] == seg_val]
                    total_start = len(df_seg)
                    df_step = df_seg.copy()
                    for col_name in selected_funnel_cols:
                        if len(df_step) == 0:
                            break
                        choice = funnel_config[col_name]
                        if choice == "[Top value]":
                            vc = df_step[col_name].value_counts(dropna=True)
                            top_value = vc.idxmax()
                        else:
                            top_value = choice
                        df_step = df_step[df_step[col_name] == top_value]

                    all_funnels.append(
                        {
                            segment_by: seg_val,
                            "start": total_start,
                            "end": len(df_step),
                            "conversion_rate": len(df_step) / total_start * 100
                            if total_start
                            else 0,
                        }
                    )

                funnels_df = pd.DataFrame(all_funnels).sort_values("conversion_rate", ascending=False)
                st.markdown("### Funnel conversion rate by segment")
                st.dataframe(funnels_df, use_container_width=True)

# ---------------------- Text Insights -----------------------
elif page == "Text Insights":
    st.title("Text Insights")

    st.markdown(
        "Basic text analysis on the open-ended question "
        "'recomendation_to_improve_attractiveness'."
    )

    text_col = "recomendation_to_improve_attractiveness"
    texts = df_filtered[text_col].dropna().astype(str).tolist()

    if len(texts) == 0:
        st.info("No text responses available with current filters.")
    else:
        st.markdown(f"Number of text answers: **{len(texts)}**")

        all_text = " ".join(texts).lower()

        keywords = {
            "price": ["price", "expensive", "cost", "budget", "prix", "moins cher", "offres", "tarifs", "coût", "abordables", "chère"],
            "language": ["language", "english", "translation", "anglais", "communiquer", "français", "langue", "anglaise", "étrangers"],
            "information": ["guide", "planning", "informée"],
            "crowd": ["crowded", "tourists", "overtourism", "moins de monde", "moins à la mode", "moins touristique"],
            "transport": ["transport", "train", "shinkansen", "flight", "métro", "vols"],
            "Do NOT Change": ["rien de plus", "attractif", "m’attirent", "rien", "sur la to do list", "perfect"]
        }

        keyword_counts = {}
        for theme, kw_list in keywords.items():
            count = sum(all_text.count(kw) for kw in kw_list)
            keyword_counts[theme] = count

        kw_df = (
            pd.DataFrame(keyword_counts.items(), columns=["theme", "count"])
            .sort_values("count", ascending=False)
        )

        fig_kw = px.bar(
            kw_df,
            x="theme",
            y="count",
            title="Keyword frequency in recommendations",
            text="count",
        )
        fig_kw.update_traces(textposition="outside")
        fig_kw.update_layout(
            xaxis_title=get_axis_label("theme"),
            yaxis_title="Keyword Count",
        )
        st.plotly_chart(fig_kw, use_container_width=True)

        st.markdown("### Raw examples")
        st.write("Here are a few random answers:")
        for t in texts[:10]:
            st.markdown(f"- {t}")

# -------------------------- Raw Data ------------------------
elif page == "Raw Data":
    st.title("Raw Data")

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
