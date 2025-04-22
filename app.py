import streamlit as st
import pandas as pd

import preprocess.preprocess as preprocess
import preprocess.sport as sport
import visualizations.scatter_charts as scatter_charts
import visualizations.sankey_diagrams as sankey_diagrams
import visualizations.bubble_chart as bubble_chart
import visualizations.connected_dot_plot as connected_dot_plot
import visualizations.stacked_bar_chart as stacked_bar_chart
import visualizations.bar_chart as bar_chart
from preprocess.preprocess import AGE_MIDPOINTS

@st.cache_data
def prep_data():
    '''
        Imports the .csv file and does some preprocessing.

        Returns:
            A pandas dataframe containing the preprocessed data.
    '''
    olympics_data_unprocessed = pd.read_csv('./assets/data/all_athlete_games.csv')
    regions_data = pd.read_csv('./assets/data/all_regions.csv')
    olympics_dataframe = preprocess.convert_age(olympics_data_unprocessed)
    olympics_dataframe = preprocess.normalize_events(olympics_dataframe)
    olympics_dataframe = preprocess.normalize_countries(olympics_dataframe, regions_data)
    
    return olympics_dataframe, regions_data

# Load the data
header_image_path = './assets/images/header_image.png'
olympics_data, regions_data = prep_data()

def main():
    # ---------------------------
    # Sidebar: User Inputs
    # ---------------------------
    st.sidebar.image(header_image_path, width=200)
    st.sidebar.title("Please provide the following details : ")
    discipline = st.sidebar.selectbox("Select a discipline", ["None"] + [sport.value for sport in sport.Sport])
    country_options = ["None"] + sorted(olympics_data["Region"].dropna().unique().tolist())
    user_country_name = st.sidebar.selectbox("Select your country", country_options)
    user_country = preprocess.get_noc_from_country(user_country_name, regions_data)
    st.sidebar.markdown("---")
    st.sidebar.markdown("[![GitHub](https://img.icons8.com/ios-glyphs/30/ffffff/github.png)](https://github.com/Mahacine/INF8808_Projet_Eq7) Developed by Team 7 : ")
    st.sidebar.code("Rima Al Zawahra 2023119\nIman Bouara 1990495\nAlexis Desforges 2146454\nMahacine Ettahri 2312965\nNeda Khoshnoudi 2252125\nNicolas Lopez 2143179")

    # ---------------------------
    # Data Filtering
    # ---------------------------
    if discipline != "None":
        filtered_discipline_data = olympics_data[olympics_data["Sport"] == discipline]

    # Header
    st.title("Welcome to our Olympics Data Exploration and Visualization App")
    st.write(f"You have selected athletes from "
             f"{user_country_name if user_country_name != 'None' else 'all countries'} in "
             f"{discipline if discipline != 'None' else 'all disciplines'}.")

    # ===========================
    # Visualization 1
    # Q1: Quel est l'âge moyen des athlètes dans ma discipline et comment a-t-il évolué au fil du temps ?
    # Q2: Quelle est la répartition de chaque catégorie d'âge ?
    # ===========================
    if discipline != "None":
        st.subheader(f"Age group distribution and average age of athletes in {discipline}:")
    else:
        st.subheader("Age group distribution and average age of athletes in my discipline :")
     
    # If a discipline is selected, filter the data and show the visualization   
    if discipline != "None":
        # Allow the user to select the mode (absolute vs relative)
        mode = st.radio("Select mode for bubble size", ("Absolute", "Relative"), key="mode_age_distribution")
        # Allow the user to show the average age line
        show_avg = st.checkbox("Show Average Age", key="show_avg_age")
        # Prepare data for visualization 1
        data_plot = preprocess.add_age_group(filtered_discipline_data)
        if data_plot.empty:
            st.info("No data available for the selected filters and age.")
        else:
            grouped = data_plot.groupby(["Year", "Age Group"]).size().reset_index(name="Count")
            grouped["Age_Midpoint"] = grouped["Age Group"].map(AGE_MIDPOINTS)

            grouped, size_column = preprocess.compute_relative_size_column(grouped, mode)
            fig1 = scatter_charts.create_age_distribution_bubble(data_plot, grouped, size_column, show_avg, mode)
            st.plotly_chart(fig1, key="fig1")
    else:
        st.info("Please select a discipline to view the age distribution and average age over time.")

    # ===========================
    # Visualization 2
    # Q4: Comment l'âge des athlètes évolue-t-il selon les sous-catégories de ma discipline ?
    # ===========================
    if discipline != "None":
        st.subheader(f"Age evolution of athletes across subcategories in {discipline} :")
    else:
        st.subheader("Age evolution of athletes across subcategories in my discipline :")
    
    # If a discipline is selected, filter the data and show the visualization 
    if discipline != "None":
        # Allow user to select a sub-category
        events = filtered_discipline_data["Event"].unique().tolist()
        event_selected = st.selectbox("Select a sub-category (Event)", ["All"] + events, key="event_select")
        
        data_event = filtered_discipline_data.copy()
        if event_selected != "All":
            data_event = data_event[data_event["Event"] == event_selected]
        
        if data_event.empty:
            st.info("No event data available for the selected filters and age.")
        else:
            grouped_event = preprocess.group_by_year_and_age_group(data_event)
            mode_event = st.radio("Select mode (Event)", ("Absolute", "Relative"), key="mode_event")
            grouped_event, size_col_event = preprocess.compute_relative_size_column(grouped_event, mode_event)
            fig2 = scatter_charts.create_event_age_scatter(grouped_event, size_col_event)
            st.plotly_chart(fig2, key="fig2")

    else:
        st.info("Please select a discipline to view sub-category analysis.")

    # ===========================
    # Visualization 3
    # Q3: Existe-t-il une tranche d'âge optimale pour remporter une médaille dans ma discipline ?
    # ===========================
    if discipline != "None":
        st.subheader(f"Optimal age range for winning a medal in {discipline} :")
    else:
        st.subheader("Optimal age range for winning a medal in my discipline :")
    
    # If a discipline is selected, filter the data and show the visualization
    if discipline != "None":
        medal_by_age_distribution = preprocess.group_by_medal_and_age_group(olympics_data[olympics_data["Sport"] == discipline])
        if medal_by_age_distribution.empty:
            st.info("No medal data available for the selected sport.")
        else:
            fig3 = bubble_chart.create_medal_age_bubble(medal_by_age_distribution)
            st.plotly_chart(fig3, key="fig3")
    else:
        st.info("Please select a discipline to view medal analysis.")

    # ===========================
    # Visualization 4
    # Q5, Q6 & Q7: Analyse de la performance et de la participation par pays via un diagramme Sankey
    # ===========================
    if user_country != "None" and discipline != "None":
        st.subheader(f"Historical performance of {user_country_name} in {discipline} vs. key reference countries :")
    else:
        st.subheader("Historical performance of my country vs. key reference countries :")
    
    # If a country and a discipline are selected, filter the data and show the visualization  
    if user_country != "None" and discipline != "None":
        # Allow the user to select the edition and the mode
        participation_year = st.selectbox("Select a year", ["All Editions"] + sorted([year for year in olympics_data["Year"].unique() if year >= 1999], reverse=True))
        performance_mode_event = st.radio("Select a mode", ("Absolute", "Relative"), key="performance_mode_event")
        if performance_mode_event == "Absolute":
            is_relative = False
        else:
            is_relative = True
        # Add the medal's legend
        st.markdown("""
        **Medal Type**<br>
        <span style="display:inline-block;width:20px;height:20px;border-radius:50%;background-color:gold;border:1px solid black;"></span> Gold<br>
        <span style="display:inline-block;width:20px;height:20px;border-radius:50%;background-color:silver;border:1px solid black;"></span> Silver<br>
        <span style="display:inline-block;width:20px;height:20px;border-radius:50%;background-color:#CD7F32;border:1px solid black;"></span> Bronze<br>
        <span style="display:inline-block;width:20px;height:20px;border-radius:50%;background-color:white;border:1px solid black;"></span> No Medal
         """, unsafe_allow_html=True)
        fig4, is_country_data_available = sankey_diagrams.create_sankey_plot(olympics_data, participation_year, discipline, user_country, is_relative)
        if fig4 is None:
            st.info("No data available for the selected filters.")
        else:
            if not is_country_data_available:            
                st.info("No data available for the selected country. However, here are the top 3 countries:")
            st.plotly_chart(fig4, key="fig4")
    else:
        st.info("Please select a country and a discipline to view performance analysis.")

    # ===========================
    # Visualization 5
    # Q8: Pour ma discipline, existe-t-il des disparités entre hommes et femmes ?
    # ===========================
    if discipline != "None":
        st.subheader(f"Disparities between men and women in {discipline} :")
    else :
        st.subheader("Disparities between men and women in my discipline :")
    
    # If a discipline is selected, filter the data and show the visualization
    if discipline != "None":
            event_counts = preprocess.dot_plot_preprocess(olympics_data, discipline)

            if "Men's" not in event_counts.columns or "Women's" not in event_counts.columns:
                st.error("There is no available data for selected discipline.")
            else:
                fig5 = connected_dot_plot.connected_dot_plot(event_counts)
                st.plotly_chart(fig5, use_container_width=True, key="fig5")
    else:
        st.info("Please select a discipline to view gender disparities.")


    # ===========================
    # Visualization 6
    # Q9 & Q10: Évolution de la répartition hommes-femmes et participation féminine dans le temps
    # ===========================
    if discipline != "None":
        st.subheader(f"Evolution of gender participation in {discipline} :")
    else :
        st.subheader("Evolution of gender participation in my discipline :")

    # If a discipline is selected, filter the data and show the visualization
    if discipline != "None":
        processed_data = preprocess.preprocess_gender_by_year(olympics_data, discipline)    
        fig6 = stacked_bar_chart.visualize_data(processed_data)
        st.plotly_chart(fig6, key="fig6")

    else:
        st.info("Please select a discipline to view gender disparities.")

    # ===========================
    # Visualization 7
    # Q11: Combien de participations un athlète dans ma discipline a-t-il généralement avant de remporter une médaille ?
    # ===========================
    if discipline != "None":
        st.subheader(f"Odds of winning a medal in {discipline} based on number of Olympic participations :")
    else :
        st.subheader("Odds of winning a medal in my discipline based on number of Olympic participations :")
    
    # If a discipline is selected, filter the data and show the visualization
    if discipline != "None":
        data = preprocess.preprocess_bar_chart_data(olympics_data, discipline)    
        fig7 = bar_chart.visualize_data(data)
        st.plotly_chart(fig7, key="fig7")

    else:
        st.info("Please select a discipline to view the odds of winning a medal.")

    # ===========================
    # Visualization 8
    # Q12: Combien de fois pourrais-je participer aux Jeux Olympiques tout au long de ma carrière ?
    # ===========================
    st.subheader("Career participation span across sports :")
    
    # If a discipline is selected, filter the data and show the visualization
    if discipline != "None":
        age_stats, age_stats_long = preprocess.preprocess_connected_dot_plot_data(olympics_data, discipline)    
        fig8 = connected_dot_plot.connected_dot_plot_8(age_stats, age_stats_long, discipline)
        st.plotly_chart(fig8, key="fig8")
    else:
        st.info("Please select a discipline to view participation span.")
        
    # ===========================
    # Visualization 9
    # Q12: Combien de fois pourrais-je participer aux Jeux Olympiques tout au long de ma carrière ?
    # ===========================  
    st.subheader("Olympic Hall of Fame :")
    
    # If a discipline is selected, filter the data and show the visualization
    if discipline != "None":
        medal_counts = preprocess.preprocess_stacked_bar_chart(olympics_data, discipline)    
        fig9 = stacked_bar_chart.stacked_bar_chart_9(medal_counts)
        st.plotly_chart(fig9, key="fig9")
    else:
        st.info("Please select a discipline to view the top athletes.")

if __name__ == "__main__":
    main()
