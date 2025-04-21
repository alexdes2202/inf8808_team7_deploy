import plotly.express as px
import style.hover_template as hover

from preprocess.preprocess import AGE_MIDPOINTS
from style.theme import GOLD, SILVER, BRONZE

medal_colors = {"Gold": GOLD, "Silver": SILVER, "Bronze": BRONZE}

def create_medal_age_bubble(grouped):
    '''
    Creates a bubble plot visualizing the distribution of medals across age groups

    args:
        grouped: Th dataFrame

    returns:
        fig: The bubble chart
    '''
    
    # Create the base scatter plot
    fig = px.scatter(grouped,
                     x="Medal",
                     y="Age_Midpoint",
                     size="Count",
                     color="Medal",
                     labels={"Medal": "Medal Type", "Age_Midpoint": "Age Group", "Count": "Number of Medalists"},
                     opacity=0.85,
                     color_discrete_map=medal_colors,
                     size_max=40)

    # Customize y-axis to show age group labels
    fig.update_yaxes(tickvals=list(AGE_MIDPOINTS.values()), ticktext=list(AGE_MIDPOINTS.keys()),
                     title="Age Group")
    
    # Order x-axis medals
    fig.update_xaxes(categoryorder="array", categoryarray=["Gold", "Silver", "Bronze"]) 
    
    # Apply the custom hover template
    fig.update_traces(hovertemplate=hover.medal_distribution_hover()) 
    
    return fig