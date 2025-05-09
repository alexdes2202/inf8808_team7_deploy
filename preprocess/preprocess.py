'''
    Contains some functions to preprocess the data used in the visualisation.
'''
import pandas as pd
import re

# Global constants for age groups
AGE_BINS = [10, 14, 17, 20, 23, 26, 30, 35, 100]
AGE_LABELS = ["10-14", "15-17", "18-20", "21-23", "24-26", "27-30", "31-35", "36+"]
AGE_MIDPOINTS = {"10-14": 12, "15-17": 16, "18-20": 19, "21-23": 22, 
                    "24-26": 25, "27-30": 28, "31-35": 33, "36+": 40}

def convert_age(df):
    '''
        Converts the 'Age' column to integer type

        args:
            df: The dataframe
        returns:
            The dataframe with 'Age' converted to integer
    '''
    df['Age'] = df['Age'].astype('Int64')
    
    return df

def normalize_events(df):
    '''
        Standardizes event names by removing redundant or repetitive sport names 
        and converting terms
        
        args:
            df: The dataframe
        returns:
            The dataframe with standardized 'Event' names
    '''
    df['Event'] = df.apply(
        lambda row: re.sub(f'^{re.escape(row["Sport"])}\\s*', '',
                        re.sub(r'\s*metres$', 'm',
                        re.sub(r'^Athletics\s*', '', row['Event']))),
        axis=1
    )
    
    return df

def normalize_countries(olympics_df, regions_df):
    '''
        Adds the country name ('Region') to the Olympics dataframe using the NOC mapping.

        args:
            olympics_df: Dataframe with Olympic data
            regions_df: Dataframe mapping 'NOC' codes to country names in a 'Region' column
        returns:
            The olympics dataframe with a new 'Region' column
    '''
    olympics_df['Region'] = olympics_df['NOC'].map(regions_df.set_index('NOC')['Region'])
    return olympics_df


def get_noc_from_country(region_name, regions_df):
    '''
        Returns the NOC code corresponding to a given country name.

        args:
            region_name: The country name
            regions_df: The dataframe containing 'Region' and 'NOC' mappings
        returns:
            The matching NOC code, or None if not found
    '''
    if region_name == "None":
        return "None"
    row = regions_df[regions_df["Region"] == region_name]
    return row["NOC"].values[0] if not row.empty else "None"


def add_age_group(df):
    '''
        Adds age group and midpoint columns to the dataframe based on predefined bins.

        args:
            df: The dataframe containing an "Age" column
        returns:
            The dataframe with "Age Group" and "Age_Midpoint" columns
    '''
    df = df.copy()
    df = df.dropna(subset=["Age"])
    
    # Categorize ages into defined bins with labels
    df["Age Group"] = pd.cut(df["Age"], bins=AGE_BINS, labels=AGE_LABELS, right=False)
    
    # Map each age group to its corresponding midpoint
    df["Age_Midpoint"] = df["Age Group"].map(AGE_MIDPOINTS)
    
    return df


def group_by_year_and_age_group(df):
    '''
        Groups the dataframe by year and age group, and counts the number of athletes in each group.

        args:
            df: The dataframe containing "Age" and "Year" columns
        returns:
            A grouped dataframe with counts and corresponding age midpoints
    '''
    df = df.copy()
    df = df.dropna(subset=["Age"])
    df["Age Group"] = pd.cut(df["Age"], bins=AGE_BINS, labels=AGE_LABELS, right=False)
    df["Age_Midpoint"] = df["Age Group"].map(AGE_MIDPOINTS)

    grouped = df.groupby(["Year", "Age Group"]).size().reset_index(name="Count")
    grouped["Age_Midpoint"] = grouped["Age Group"].map(AGE_MIDPOINTS)

    return grouped


def compute_relative_size_column(df, mode, value_col="Count", group_col="Year"):
    '''
        Computes relative percentages if mode is set to "Relative", otherwise returns absolute counts.

        args:
            df: The dataframe with a column to be used for sizing (e.g., "Count")
            mode: Either "Absolute" or "Relative"
            value_col: The column to compute percentage from (default "Count")
            group_col: The grouping column for relative computation (default "Year")
        returns:
            The updated dataframe and the name of the column to use for bubble size
    '''
    if mode == "Relative":
        # Calculate total value per group
        total_per_group = df.groupby(group_col)[value_col].transform("sum")
        # Compute percentage contribution within each group
        df["Percentage"] = ((df[value_col] / total_per_group) * 100).round(2)
        return df, "Percentage"
    else:
        return df, value_col

def preprocess_sankey_data(olympics_data, year, sport, country, top_k=3):
    '''
        Computes data to display in the participation sankey diagram

        args:
            olympics_data: The dataframe 
            year: The participation year
            sport: The selected discipline
            country: The participating country
            top_k: 
        returns:
            The constructed Sankey diagram
    '''
    
    # If the selected year is "All Editions", include all years
    if year == "All Editions":
        df_medals = olympics_data[(olympics_data["Sport"] == sport)]
    else:
        df_medals = olympics_data[(olympics_data["Sport"] == sport) & (olympics_data["Year"] == year)]

    # Count the number of medals for each country
    df_medals_with_medals = df_medals[df_medals['Medal'].notna()]
    total_medal_counts = df_medals_with_medals['NOC'].value_counts()
    # Select the 'country' and the top k countries
    top_countries = total_medal_counts.head(top_k).index.tolist()
    if country not in top_countries:
        top_countries.append(country)

    # Keep only the previous countries
    df_medals = df_medals[df_medals['NOC'].isin(top_countries)]

    # Create No Medal label for NaN values
    df_medals['Medal'] = df_medals['Medal'].fillna('No Medal')

    # Create a column to differiente each country and their medals
    # This will be used to map each country to its own nodes in the sankey diagram
    df_medals['Medal_NOC'] = df_medals['Medal'] + '_' + df_medals['NOC']

    # Count the number of medals for each country, for each type of medals
    medal_counts = df_medals.groupby(['NOC', 'Region', 'Medal_NOC']).size().reset_index(name='Count')

    total_counts_per_country = df_medals.groupby('NOC').size()  # Total participations per country
    print(total_counts_per_country)
    if total_counts_per_country.empty:
        return None, None
    
    medal_counts['Percentage'] = medal_counts.apply(lambda row: (row['Count'] / total_counts_per_country[row['NOC']]) * 100, axis=1)  # Normalize to percentage

    # Sort countries
    total_counts_sorted = medal_counts.groupby('NOC')['Count'].sum().sort_values(ascending=False)
    sorted_countries = total_counts_sorted.index.tolist()

    medal_counts['NOC'] = pd.Categorical(medal_counts['NOC'], categories=sorted_countries, ordered=True)
    medal_counts = medal_counts.sort_values('NOC')

    return df_medals, medal_counts

def group_by_medal_and_age_group(df):
    '''
        Groups the dataframe by year and age group, and counts the number of medals in each group.

        args:
            df: The dataframe containing "Age" and "Medal" columns
        returns:
            A grouped dataframe with medal counts
    '''
    df = df.copy()
    df = df.dropna(subset=["Age"])
    df["Age Group"] = pd.cut(df["Age"], bins=AGE_BINS, labels=AGE_LABELS, right=False)
    df["Age_Midpoint"] = df["Age Group"].map(AGE_MIDPOINTS)
    grouped = df.groupby(["Medal", "Age Group"]).size().reset_index(name="Count")
    grouped["Age_Midpoint"] = grouped["Age Group"].map(AGE_MIDPOINTS)
    
    return grouped


def dot_plot_preprocess(olympics_data, discipline):
    '''
        Prepares event data for the dot plot showing gender disparities.

        args:
            olympics_data: Olympics dataframe
            discipline: The selected sport discipline
        returns:
            A dataframe counting events per gender
    '''
    sport_events = olympics_data[olympics_data["Sport"] == discipline]["Event"]
    df = pd.DataFrame(sport_events, columns=['Event'])

    # Clean and categorize the data
    df['Clean_Event'] = df['Event'].str.replace(r"Men's |Women's |Mixed ", '', regex=True)
    df['Gender'] = df['Event'].str.extract(r"(Men's|Women's)")

    # Create a pivot table to count events by gender
    event_counts = df.pivot_table(index='Clean_Event', columns='Gender', aggfunc='size', fill_value=0).reset_index()
    
    return event_counts

def preprocess_gender_by_year(data, sport):
    '''
        Process gender participation data over the years for a stacked bar chart.

        args:
            data: Olympics dataframe
            sport: The selected sport discipline
        returns:
            A pivoted dataframe with male/female participation percentages per year
    '''
    athletics_data = data[data["Sport"] == sport]
    # Count number of entries by Year and Gender
    gender_counts = athletics_data.groupby(["Year", "Gender"]).size().reset_index(name="Count")

    pivot_df = gender_counts.pivot(index="Year", columns="Gender", values="Count").fillna(0)
    # Calculate total participants per year
    pivot_df["Total"] = pivot_df.sum(axis=1)
    # Compute percentage of female and male participants
    pivot_df["Female %"] = (pivot_df["Female"] / pivot_df["Total"]) * 100
    pivot_df["Male %"] = (pivot_df["Male"] / pivot_df["Total"]) * 100

    pivot_df = pivot_df.reset_index()
    pivot_df["Year"] = pivot_df["Year"].astype(str)
    
    return pivot_df

def preprocess_bar_chart_data(olympics_data, sport):
    '''
        Computes data to display in the 

        args:
            olympics_data: The dataframe 
            sport: The selected discipline
        returns:
            Data for the Visualisation 7 bar chart
    '''
    df = olympics_data[olympics_data["Sport"] == sport].sort_values(["Name", "Year"])

    # Count number of participations per athlete
    df["Participation_Number"] = df.groupby("Name").cumcount() + 1 
    df["Medal_Status"] = df["Medal"].apply(lambda x: "Medal Won" if pd.notna(x) else "No Medal")
    df["Medal"] = df["Medal"].fillna("No Medal")

    # Aggregate counts by number of participations and medal status
    participation_counts = df.groupby(["Participation_Number", "Medal_Status"]).size().unstack(fill_value=0)
    participation_counts = participation_counts.reset_index()
    participation_counts_detailed = df.groupby(["Sport", "Participation_Number", "Medal"]).size().unstack(fill_value=0)
    participation_counts_detailed = participation_counts_detailed[["Gold", "Silver", "Bronze", "No Medal"]].reset_index()
    
    sport_selected_medals = participation_counts_detailed

    # Calculate percentage of each medal type
    sport_selected_medals['Gold_Percentage'] = (sport_selected_medals['Gold'] / (sport_selected_medals['Gold'] + sport_selected_medals['Silver'] + sport_selected_medals['Bronze'] + sport_selected_medals['No Medal'])) * 100
    sport_selected_medals['Silver_Percentage'] = (sport_selected_medals['Silver'] / (sport_selected_medals['Gold'] + sport_selected_medals['Silver'] + sport_selected_medals['Bronze'] + sport_selected_medals['No Medal'])) * 100
    sport_selected_medals['Bronze_Percentage'] = (sport_selected_medals['Bronze'] / (sport_selected_medals['Gold'] + sport_selected_medals['Silver'] + sport_selected_medals['Bronze'] + sport_selected_medals['No Medal'])) * 100
    
    df = sport_selected_medals[sport_selected_medals['Participation_Number'] <= 4] 
    
    return df

def preprocess_connected_dot_plot_data(olympics_data, sport):
    '''
        Prepares min and max age data for each sport

        args:
            olympics_data: Olympics dataframe
            sport: The selected sport to highlight in the visualization

        returns:
            age_stats: Dataframe with min/max ages and colors for each sport
            age_stats_long: Melted version for plotting
    '''

    df = olympics_data
    
    df['Career Length'] = df.groupby('Name')['Year'].transform('nunique')
    
    # Get minimum and maximum age per sport
    min_age = df.groupby('Sport')['Age'].min().reset_index()
    max_age = df.groupby('Sport')['Age'].max().reset_index()
    age_stats = pd.merge(min_age, max_age, on='Sport', suffixes=('_min', '_max'))

    # Highlight the selected sport in red, others in gray
    age_stats['Color'] = age_stats['Sport'].apply(lambda x: 'red' if x == sport else 'gray')

    # Reshape the data for plotting
    age_stats_long = pd.melt(
        age_stats,
        id_vars=['Sport', 'Color'],
        value_vars=['Age_min', 'Age_max'],
        var_name='Age',
        value_name='Age (Years)'
    )
    return age_stats, age_stats_long   


def preprocess_stacked_bar_chart(olympics_data, sport):
    '''
        Returns the count of medals per athlete for a given sport

        args:
            olympics_data: Olympics dataframe
            sport: The selected sport to filter on

        returns:
            medal_counts: Dataframe with number of medals per athlete by medal type
    '''

    df = olympics_data[olympics_data["Sport"] == sport]
    
    df["Medal"] = df["Medal"].fillna("No Medal")

    medal_counts = df[df["Medal"] != "No Medal"].groupby(["Name", "Medal"]).size().reset_index(name="Count")
    
    return medal_counts