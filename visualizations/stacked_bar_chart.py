import plotly.express as px
from style.theme import MALE, FEMALE, GOLD, SILVER, BRONZE

def visualize_data(data):
    '''
    Creates a bar chart showing the percentage of male and female athletes participating in 
    the Olympics over the years

    Args:
        data: The dataframe for the selected sport

    Returns:
        The participation ratio stacked bar chart
    '''
    
    # Create a bar chart for male and female participation percentages per year
    fig = px.bar(
        data,
        x="Year",
        y=["Female %", "Male %"],
        labels={"value": "Percentage of Athletes", "Year": "Olympic Year"},
        color_discrete_map={"Female %": FEMALE, "Male %": MALE}
    )

    # Customize layout with relative bar mode, legend, and axis labels
    fig.update_layout(
        barmode="relative",
        legend_title=dict(
            text="Gender",
            font=dict(size=14)
        ),
        xaxis=dict(
            type="category",
            tickmode="array",
            tickvals=data["Year"],
            ticktext=data["Year"],
            tickfont=dict(size=14),         
        ),
        yaxis=dict(
            title="Percentage of Participation",
            tickfont=dict(size=14)          
        ),
        plot_bgcolor="#f0f0f0",
    )

    # Add a horizontal line at 50% participation
    fig.add_hline(y=50, line_dash="dash", line_color="black", annotation_text="50%",
                  annotation_position="right", annotation_font_size=14, annotation_font_color="black")

    fig.update_xaxes(tickangle=-90)

    return fig

def stacked_bar_chart_9(medal_counts):
    '''
    Creates a horizontal stacked bar chart showing the total number of medals won
    by the top 10 athletes

    Args:
        medal_counts : DataFrame containing athlete names, medal types, and counts

    Returns:
        The stacked bar chart with medal distribution of top 10 athletes
    '''
    
    # Identify top 10 athletes by total medal count
    top_athletes = medal_counts.groupby("Name")["Count"].sum().nlargest(10)
    medal_counts = medal_counts[medal_counts["Name"].isin(top_athletes.index)]
    medal_colors = {"Gold": GOLD, "Silver": SILVER, "Bronze": BRONZE}

    # Reverse the order
    ordered_athletes = top_athletes.index[::-1]
    
    # Create the horizontal stacked bar chart 
    fig = px.bar(
        medal_counts,
        x="Count",
        y="Name",
        color="Medal",
        orientation="h",
        labels={"Count": "Total Medals", "Name": "Athletes"},
        color_discrete_map=medal_colors,
        category_orders={"Name": ordered_athletes}
    )

    # Customize layout : axis labels, legend and template
    fig.update_layout(
        template="plotly_white",
        xaxis_title="Total Medals",
        yaxis_title="",
        showlegend=True
    )
    
    return fig