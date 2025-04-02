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
   
    df['Age'] = df['Age'].astype('Int64')
    
    return df

def normalize_events(df):
    
    df['Event'] = df.apply(
        lambda row: re.sub(f'^{re.escape(row["Sport"])}\\s*', '',
                        re.sub(r'\s*metres$', 'm',
                        re.sub(r'^Athletics\s*', '', row['Event']))),
        axis=1
    )
    
    return df

def normalize_countries(olympics_df, regions_df):
    
    olympics_df['Region'] = olympics_df['NOC'].map(regions_df.set_index('NOC')['Region'])
    return olympics_df


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
    df["Age Group"] = pd.cut(df["Age"], bins=AGE_BINS, labels=AGE_LABELS, right=False)
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
        total_per_group = df.groupby(group_col)[value_col].transform("sum")
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
    medal_counts = df_medals.groupby(['NOC', 'Medal_NOC']).size().reset_index(name='Count')

    total_counts_per_country = df_medals.groupby('NOC').size()  # Total participations per country
    print(total_counts_per_country)
    if total_counts_per_country.empty:
        return None, None
    
    # print(year)
    # print(medal_counts.apply(lambda row: (row['Count'] / total_counts_per_country[row['NOC']]) * 100, axis=1))
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
    sport_events = olympics_data[olympics_data["Sport"] == discipline]["Event"]
    df = pd.DataFrame(sport_events, columns=['Event'])

    # Cleaning and categorizing the data
    df['Clean_Event'] = df['Event'].str.replace(r"Men's |Women's |Mixed ", '', regex=True)
    df['Gender'] = df['Event'].str.extract(r"(Men's|Women's)")

    # Creating a pivot table to count events by gender
    event_counts = df.pivot_table(index='Clean_Event', columns='Gender', aggfunc='size', fill_value=0).reset_index()
    
    return event_counts