import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

import preprocess
import sport
import scatter_charts
import sankey_diagrams
import bubble_chart
import connected_dot_plot
from preprocess import AGE_MIDPOINTS, AGE_LABELS, AGE_BINS

def prep_data(olympics_dataframe, regions_dataframe):
    '''
        Imports the .csv file and does some preprocessing.

        Returns:
            A pandas dataframe containing the preprocessed data.
    '''
    
    olympics_dataframe = preprocess.convert_age(olympics_dataframe)
    olympics_dataframe = preprocess.normalize_events(olympics_dataframe)
    olympics_dataframe = preprocess.normalize_countries(olympics_dataframe, regions_dataframe)
    
    return olympics_dataframe

# Load the data
olympics_data_unprocessed = pd.read_csv('./assets/data/all_athlete_games.csv')
regions_data = pd.read_csv('./assets/data/all_regions.csv')

header_image_path = './assets/images/header_image.png'

olympics_data = prep_data(olympics_data_unprocessed, regions_data)

def main():
    # ---------------------------
    # Sidebar: User Inputs
    # ---------------------------
    st.sidebar.image(header_image_path, width=200)
    st.sidebar.title("Please provide the following details : ")
    user_sex = st.sidebar.selectbox("Select your sex", ["Male", "Female"])
    discipline = st.sidebar.selectbox("Select a discipline", ["None"] + [sport.value for sport in sport.Sport])
    user_country = st.sidebar.selectbox("Select your country", ["None"] + olympics_data["NOC"].unique().tolist())
    user_age = st.sidebar.text_input("Enter your age (0-99)")
    st.sidebar.markdown("---")
    st.sidebar.markdown("[![GitHub](https://img.icons8.com/ios-glyphs/30/ffffff/github.png)](https://github.com/Mahacine/INF8808_Projet_Eq7) Developed by Team 7 : ")
    st.sidebar.code("Rima Al Zawahra 2023119\nIman Bouara 1990495\nAlexis Desforges 2146454\nMahacine Ettahri 2312965\nNeda Khoshnoudi 2252125\nNicolas Lopez 2143179")

    # Validate age input
    if user_age:
        if user_age.isdigit():
            user_age = int(user_age)
            if user_age < 0 or user_age > 99:
                st.sidebar.error("Age must be between 0 and 99.")
                return
        else:
            st.sidebar.error("Please enter a valid age.")
            return
    else:
        user_age = None

    # ---------------------------
    # Data Filtering
    # ---------------------------
    if discipline != "None" and user_country != "None":
        filtered_data = olympics_data[(olympics_data["Sport"] == discipline) & 
                                      (olympics_data["Gender"] == user_sex) & 
                                      (olympics_data["NOC"] == user_country)]
    elif discipline != "None":
        filtered_data = olympics_data[(olympics_data["Sport"] == discipline) & 
                                      (olympics_data["Gender"] == user_sex)]
    elif user_country != "None":
        filtered_data = olympics_data[(olympics_data["Gender"] == user_sex) & 
                                      (olympics_data["NOC"] == user_country)]
    else:
        filtered_data = olympics_data[olympics_data["Gender"] == user_sex]

    if user_age is not None:
        filtered_data = filtered_data[filtered_data["Age"] == user_age]

    # Header
    st.title("Welcome to our Olympics Data Exploration and Visualization App")
    st.write(f"You have selected {user_sex} athletes from "
             f"{user_country if user_country != 'None' else 'all countries'} in "
             f"{discipline if discipline != 'None' else 'all disciplines'}.")

    # ===========================
    # Visualization 1
    # Q1: Quel est l'âge moyen des athlètes dans ma discipline et comment a-t-il évolué au fil du temps ?
    # Q2: Quelle est la répartition de chaque catégorie d'âge ?
    # ===========================
    st.subheader("Visualization 1: Quel est l'âge moyen des athlètes dans ma discipline et comment a-t-il évolué au fil du temps et quelle est la répartition de chaque catégorie d'âge ?")
    # Interactive controls: absolute vs relative and option to overlay average age
    mode = st.radio("Select mode for bubble size", ("Absolute", "Relative"), key="mode_age_distribution")
    show_avg = st.checkbox("Show Average Age", key="show_avg_age")

    # Prepare data for visualization 1
    data_plot = preprocess.add_age_group(filtered_data)
    if data_plot.empty:
        st.info("No data available for the selected filters and age.")
    else:
        grouped = data_plot.groupby(["Year", "Age Group"]).size().reset_index(name="Count")
        grouped["Age_Midpoint"] = grouped["Age Group"].map(AGE_MIDPOINTS)

        grouped, size_column = preprocess.compute_relative_size_column(grouped, mode)

        fig1 = scatter_charts.create_age_distribution_bubble(data_plot, grouped, size_column, show_avg, mode)
        st.plotly_chart(fig1)

    # ===========================
    # Visualization 2
    # Q4: Comment l'âge des athlètes évolue-t-il selon les sous-catégories de ma discipline ?
    # ===========================
    st.subheader("Visualisation 2: Comment l'âge des athlètes évolue-t-il selon les sous-catégories de ma discipline ?")
    if discipline != "None":
        events = filtered_data["Event"].unique().tolist()
        event_selected = st.selectbox("Select a sub-category (Event)", ["All"] + events, key="event_select")
        
        data_event = filtered_data.copy()
        if event_selected != "All":
            data_event = data_event[data_event["Event"] == event_selected]
        
        if data_event.empty:
            st.info("No event data available for the selected filters and age.")
        else:
            grouped_event = preprocess.group_by_year_and_age_group(data_event)
            mode_event = st.radio("Select mode (Event)", ("Absolute", "Relative"), key="mode_event")
            grouped_event, size_col_event = preprocess.compute_relative_size_column(grouped_event, mode_event)
            fig2 = scatter_charts.create_event_age_scatter(grouped_event, size_col_event)
            st.plotly_chart(fig2)

    else:
        st.info("Please select a discipline to view sub-category analysis.")

    # ===========================
    # Visualization 3
    # Q3: Existe-t-il une tranche d'âge optimale pour remporter une médaille dans ma discipline ?
    # ===========================
    st.subheader("Visualisation 3: Existe-t-il une tranche d'âge optimale pour remporter une médaille dans ma discipline ?")
    if discipline != "None":
        medal_by_age_distribution = preprocess.group_by_medal_and_age_group(olympics_data[olympics_data["Sport"] == discipline])
        if medal_by_age_distribution.empty:
            st.info("No medal data available for the selected sport.")
        else:
            fig3 = bubble_chart.create_medal_age_bubble(medal_by_age_distribution)
            st.plotly_chart(fig3)
    else:
        st.info("Please select a discipline to view medal analysis.")

    # ===========================
    # Visualization 4
    # Q5, Q6 & Q7: Analyse de la performance et de la participation par pays via un diagramme Sankey
    # ===========================
    st.subheader("Visualisation 4: Comment mon pays a-t-il performé historiquement et comparativement aux pays de référence ?")
    if user_country != "None" and discipline != "None":
        participation_year = st.selectbox("Select a year", ["All Editions"] + sorted([year for year in olympics_data["Year"].unique() if year >= 1999], reverse=True))
        performance_mode_event = st.radio("Select a mode", ("Absolute", "Relative"), key="performance_mode_event")
        if performance_mode_event == "Absolute":
            is_relative = False
        else:
            is_relative = True
        # Add a legend
        st.markdown("""
        **Medal Type**  
        <span style="display:inline-block;width:20px;height:20px;border-radius:50%;background-color:gold;border:1px solid black;"></span> **Gold**  
        <span style="display:inline-block;width:20px;height:20px;border-radius:50%;background-color:silver;border:1px solid black;"></span> **Silver**  
        <span style="display:inline-block;width:20px;height:20px;border-radius:50%;background-color:#CD7F32;border:1px solid black;"></span> **Bronze**  
        <span style="display:inline-block;width:20px;height:20px;border-radius:50%;background-color:white;border:1px solid black;"></span> **No Medal**
        """, unsafe_allow_html=True)
        fig4 = sankey_diagrams.create_sankey_plot(olympics_data, participation_year, discipline, user_country, is_relative)
        if fig4 is None:
            st.info("No data available for the selected filters.")
        else:
            st.plotly_chart(fig4)
    else:
        st.info("Please select a country and a discipline to view performance analysis.")

    # ===========================
    # Visualization 5
    # Q8: Pour ma discipline, existe-t-il des disparités entre hommes et femmes ?
    # ===========================
    st.subheader("Visualisation 5: Pour ma discipline, existe-t-il des disparités entre hommes et femmes ?")

    if discipline != "None":
            event_counts = preprocess.dot_plot_preprocess(olympics_data, discipline)

            if "Men's" not in event_counts.columns or "Women's" not in event_counts.columns:
                st.error("There is no available data for selected discipline.")
            else:
                fig5 = connected_dot_plot.connected_dot_plot(event_counts, discipline)
                st.plotly_chart(fig5, use_container_width=True)
    else:
        st.info("Please select a discipline to view gender disparities.")


    # ===========================
    # Visualization 6
    # Q9 & Q10: Évolution de la répartition hommes-femmes et participation féminine dans le temps
    # ===========================
    st.subheader("Visualisation 6: Evolution of Gender Participation Over Time")
    if discipline != "None":
        data_gender = olympics_data[(olympics_data["Sport"] == discipline) & 
                                    (olympics_data["Gender"].isin(["Male", "Female"]))].copy()
    else:
        data_gender = olympics_data[olympics_data["Gender"].isin(["Male", "Female"])].copy()
    gender_year = data_gender.groupby(["Year", "Gender"]).size().reset_index(name="Count")
    year_totals = gender_year.groupby("Year")["Count"].transform("sum")
    gender_year["Percentage"] = (gender_year["Count"] / year_totals) * 100
    fig6 = px.bar(gender_year, x="Year", y="Percentage", color="Gender", barmode="stack",
                  labels={"Percentage": "Percentage of Participants", "Year": "Year"},
                  title="Gender Participation Over Time",
                  color_discrete_map={"Male": "blue", "Female": "pink"})
    fig6.add_hline(y=50, line_dash="dash", line_color="black")
    st.plotly_chart(fig6)

    # ===========================
    # Visualization 7
    # Q11: Combien de participations un athlète dans ma discipline a-t-il généralement avant de remporter une médaille ?
    # ===========================
    # Visualization: Number of Medals Over Time
    df = olympics_data[olympics_data["Gender"] == user_sex]

    if discipline != "None":
        df = olympics_data[olympics_data["Sport"] == discipline].copy()
    else :
        df = olympics_data[olympics_data["Sport"] == "Ice Hockey"].copy()

    if user_country: 
        df = df[df["NOC"].isin(["CAN", "USA", user_country])]
    else:
        df = df[df["NOC"].isin(["CAN", "USA"])]

    # Filter for user sex
    
    
    df = df.drop_duplicates(subset=["Name", "Year"])
    df = df.sort_values(["Name", "Year"])
    df["Participation_Number"] = df.groupby("Name").cumcount() + 1
    df["Participation_Number"] = df["Participation_Number"].apply(lambda x: str(x) if x <= 3 else "4+")
    df["Medal_Status"] = df["Medal"].apply(lambda x: "Medal Won" if pd.notna(x) else "No Medal")

    participation_counts = df.groupby(["Team", "Participation_Number", "Medal_Status"]).size().unstack(fill_value=0)
    odds_by_part = participation_counts.iloc[:, 0].div(participation_counts.sum(axis=1), axis=0) * 100
    odds_by_part = odds_by_part.reset_index(name="Odds")
    team_indices = {team: idx for idx, team in enumerate(odds_by_part["Team"].unique())}
    odds_by_part["y"] = odds_by_part["Team"].map(team_indices)
    num_teams = len(team_indices)
    fig_height = 400 + num_teams * 50  # Base height of 400 plus 50 per team
    
    fig = px.scatter(
        odds_by_part,
        x="Participation_Number",
        y="y",  # Use y values based on team index
        size="Odds",
        color="Team",
        text=odds_by_part["Odds"].round(2).astype(str) + '%',  # Add percentage labels
        labels={"Participation_Number": "Number of Olympic Participations", "Odds": "Odds of Winning a Medal (1/x)"},
        opacity=0.85,
        size_max=75,
        height=fig_height  # Set the height of the figure
    )
    
    fig.update_layout(
        font=dict(size=14),
        xaxis=dict(
            showline=False,
            showgrid=False,
            tickmode="array",
            tickvals=["1", "2", "3", "4+"],
            ticktext=["1", "2", "3", "4+"]
        ),
        yaxis=dict(visible=False),  # Hide the y-axis
        showlegend=True  # Show the legend
    )
    st.subheader("Visualisation 7: Odds of Winning a Medal Based on Number of Olympic Participations" + (f" in {discipline}" if discipline != "None" else " in Ice Hockey")+ (f" for {user_sex}")) 
    st.plotly_chart(fig)

    # ===========================
    # Visualization 8
    # Q12: Combien de fois pourrais-je participer aux Jeux Olympiques tout au long de ma carrière ?
    # ===========================
    st.subheader("Visualisation 8: Career Participation Span Across Sports")
    career_data = olympics_data.groupby("Sport")["Age"].agg(Min_Age="min", Max_Age="max").reset_index()
    fig8 = go.Figure()
    for i, row in career_data.iterrows():
        color = "red" if (discipline != "None" and row["Sport"] == discipline) else "blue"
        fig8.add_trace(go.Scatter(
            x=[row["Sport"], row["Sport"]],
            y=[row["Min_Age"], row["Max_Age"]],
            mode="lines+markers",
            line=dict(dash="dot", color=color),
            marker=dict(size=10, color=color),
            showlegend=False
        ))
    fig8.update_layout(
        xaxis_title="Sport",
        yaxis_title="Age",
        title="Career Participation Span by Sport",
        xaxis_tickangle=-45
    )
    st.plotly_chart(fig8)

if __name__ == "__main__":
    main()
