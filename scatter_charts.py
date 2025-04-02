'''
    Contains the functions to set up the scatter plot visualization.
'''

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import hover_template as hover

from preprocess import AGE_MIDPOINTS

def add_age_distribution_trace(fig, grouped, size_column, mode="Absolute", show_avg=False):
    '''
    Adds scatter bubbles for age distribution to the figure.
    '''
    fig.add_trace(
        go.Scatter(
            x=grouped["Year"],
            y=grouped["Age_Midpoint"],
            mode="markers",
            marker=dict(
                size=grouped[size_column],
                sizemode="area",
                sizeref=2.*max(grouped[size_column])/(40.**2),
                sizemin=4,
                color=grouped["Age_Midpoint"],
                colorscale="Viridis",
                showscale=True,
            ),
            name="Age Group",
            hovertemplate=hover.age_distribution_hover(mode),
        ),
        secondary_y=False if show_avg else None
    )
    return fig


def add_avg_age_trace(fig, data):
    '''
    Adds the average age line plot to the figure.
    '''
    avg_age = data.groupby("Year")["Age"].mean().reset_index(name="Average Age")
    fig.add_trace(
        go.Scatter(
            x=avg_age["Year"],
            y=avg_age["Average Age"],
            mode="lines+markers",
            name="Average Age",
            line=dict(color="red"),
        ),
        secondary_y=True
    )
    return fig


def format_age_yaxes(fig, show_avg=False):
    '''
    Updates y-axes for displaying age group and/or average age.
    '''
    if show_avg:
        fig.update_yaxes(title_text="Age Group (Midpoint)", secondary_y=False,
                         tickvals=list(AGE_MIDPOINTS.values()), ticktext=list(AGE_MIDPOINTS.keys()))
        fig.update_yaxes(title_text="Average Age", secondary_y=True)
    else:
        fig.update_yaxes(title_text="Age Group (Midpoint)",
                         tickvals=list(AGE_MIDPOINTS.values()), ticktext=list(AGE_MIDPOINTS.keys()))
    return fig


def create_age_distribution_bubble(data, grouped, size_column, show_avg=False, mode="Absolute"):
    '''
    Creates the age distribution bubble chart (Visualization 1).
    '''
    if grouped.empty:
        return go.Figure().update_layout(title="No data available for the selected filters.")

    fig = make_subplots(specs=[[{"secondary_y": True}]]) if show_avg else go.Figure()
    fig = add_age_distribution_trace(fig, grouped, size_column, mode, show_avg)
    if show_avg:
        fig = add_avg_age_trace(fig, data)
    fig = format_age_yaxes(fig, show_avg)
    fig.update_layout(
        title="Evolution of Age Distribution and Average Age Over Time",
        xaxis_title="Year",
        legend_title="Legend"
    )
    return fig



def create_event_age_scatter(grouped_event, size_col):
    '''
    Creates a scatter plot of age distribution across events (Visualization 2).
    '''
    fig = px.scatter(grouped_event,
                     x="Year",
                     y="Age_Midpoint",
                     size=size_col,
                     color="Age Group",
                     labels={"Year": "Year", "Age Group": "Age Group", 
                             size_col: "Percentage" if size_col == "Percentage" else "Count"},
                     opacity=0.85,
                     size_max=40)

    fig.update_yaxes(tickvals=list(AGE_MIDPOINTS.values()), ticktext=list(AGE_MIDPOINTS.keys()),
                     title="Age Group (Midpoint)")
    return fig