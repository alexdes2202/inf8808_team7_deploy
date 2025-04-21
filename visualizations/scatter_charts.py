import plotly.graph_objects as go
import plotly.express as px
import style.hover_template as hover
import pandas as pd

from preprocess.preprocess import AGE_MIDPOINTS, AGE_BINS, AGE_LABELS

def add_age_distribution_trace(fig, grouped, size_column, mode="Absolute", show_avg=False):
    '''
    Adds scatter bubbles for age distribution to the figure.

    Args:
        fig: The Plotly figure to add the trace to
        grouped: Grouped data by year and age group
        size_column: Column name for bubble sizes ("Count" or "Percentage")
        mode: Mode used for bubble size ("Absolute" or "Relative")
        show_avg: Whether or not average age is displayed

    Returns:
        The updated figure with the added trace
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
                showscale=False,
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

        Args:
        fig: The Plotly figure to add the trace to
        data: filtered data

        Returns:
            The updated figure with the average age line trace
    '''
    avg_age = data.groupby("Year")["Age"].mean().reset_index()
    avg_age["Age Group"] = pd.cut(
        avg_age["Age"], bins=AGE_BINS, labels=AGE_LABELS, right=False
    )
    avg_age["Age_Midpoint"] = avg_age["Age Group"].map(AGE_MIDPOINTS)
    
    scatter_trace = go.Scatter(
        x=avg_age["Year"],
        y=avg_age["Age_Midpoint"],
        mode="lines+markers",
        name="Average Age",
        line=dict(color="red"),
    )

    fig.add_trace(scatter_trace)
    
    return fig


def format_age_yaxes(fig, show_avg=False):
    '''
        Updates y-axes for displaying age group and/or average age.
        
        Args:
        fig: The Plotly figure to format
        show_avg: Whether average age is also displayed on a secondary y-axis

        Returns:
            The updated figure with formatted y-axes
    '''
    if show_avg:
        # Update the primary y-axis to show age groups
        fig.update_yaxes(title_text="Age Group (Midpoint)", secondary_y=False,
                         tickvals=list(AGE_MIDPOINTS.values()), ticktext=list(AGE_MIDPOINTS.keys()))
        # Add a secondary y-axis to display the average age
        fig.update_yaxes(title_text="Average Age", secondary_y=True,
                         tickvals=list(AGE_MIDPOINTS.values()), ticktext=list(AGE_MIDPOINTS.keys()))
    else:
        fig.update_yaxes(title_text="Age Group (Midpoint)",
                         tickvals=list(AGE_MIDPOINTS.values()), ticktext=list(AGE_MIDPOINTS.keys()))
    return fig


def create_age_distribution_bubble(data, grouped, size_column, show_avg=False, mode="Absolute"):
    '''
    Creates the age distribution bubble chart (Visualization 1).

    Args:
        data: filtered data
        grouped: Data grouped by year and age group.
        size_column: Column to use for bubble size ("Count" or "Percentage").
        show_avg: Whether to show the average age line.
        mode: "Absolute" or "Relative", for hover info and sizing.

    Returns:
        A Plotly figure showing the age distribution and average age if enabled
    '''
    # If no grouped data, return an empty figure with a message
    if grouped.empty:
        return go.Figure().update_layout(title="No data available for the selected filters.")
    
    # Create the scatter plot for age distribution and use size and color for the bubbles
    fig = px.scatter(
        grouped,
        x="Year",
        y="Age_Midpoint",
        size=size_column,
        color="Age Group",
        labels={"Year": "Year", "Age Group": "Age Group", size_column: "Count" if mode == "Absolute" else "Percentage"},
        opacity=0.85,
        size_max=40
    )
    
    # Update the y-axis to show the age groups
    fig.update_yaxes(
        tickvals=list(AGE_MIDPOINTS.values()),
        ticktext=list(AGE_MIDPOINTS.keys()),
        title="Age Group (Midpoint)"
    )

    # Add a line for the average age
    if show_avg:
        avg_age = data.groupby("Year")["Age"].mean().reset_index(name="Average Age")
        fig.add_trace(
            go.Scatter(
                x=avg_age["Year"],
                y=avg_age["Average Age"],
                mode="lines+markers",
                name="Average Age",
                line=dict(color="red")
            )
        )

    return fig


def create_event_age_scatter(grouped_event, size_col):
    '''
    Creates a scatter plot of age distribution across events (Visualization 2).
    
    Args:
        grouped_event: Grouped data by year and age group for events.
        size_col: Column name to use for bubble size ("Count" or "Percentage").

    Returns:
        go.Figure: A Plotly Express scatter figure for age distribution across events.
    '''
    # Create the scatter plot for age distribution and use size and color for the bubbles
    fig = px.scatter(grouped_event,
                     x="Year",
                     y="Age_Midpoint",
                     size=size_col,
                     color="Age Group",
                     labels={"Year": "Year", "Age Group": "Age Group", 
                             size_col: "Percentage" if size_col == "Percentage" else "Count"},
                     opacity=0.85,
                     size_max=40)

    # Update the y-axis to show the age groups
    fig.update_yaxes(tickvals=list(AGE_MIDPOINTS.values()), ticktext=list(AGE_MIDPOINTS.keys()),
                     title="Age Group (Midpoint)")
    return fig