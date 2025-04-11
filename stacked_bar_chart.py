# import plotly.express as px

# def visualize_data(data):
#     fig = px.bar(
#         data,
#         x="Year",
#         y=["Female %", "Male %"],
#         labels={"value": "Percentage of Athletes", "Year": "Olympic Year"},
#         title="Evolution of Male and Female Participation in Olympic Athletics",
#         color_discrete_map={"Female %": "pink", "Male %": "blue"}
#     )

#     fig.update_layout(
#         barmode="relative",
#         xaxis=dict(
#             type="category",
#             tickmode="array",
#             tickvals=data["Year"],
#             ticktext=data["Year"],
#         ),
#         yaxis=dict(title="% Share of Athletes"),
#         plot_bgcolor="white"
#     )

#     fig.add_hline(y=50, line_dash="dash", line_color="black", annotation_text="50%",
#                   annotation_position="right", annotation_font_size=14, annotation_font_color="black")

#     fig.update_xaxes(tickangle=-90)

#     fig.show()

import plotly.express as px


def visualize_data(data, sport):
    fig = px.bar(
        data,
        x="Year",
        y=["Female %", "Male %"],
        labels={"value": "Percentage of Athletes", "Year": "Olympic Year"},
        # title=f"Evolution of Male and Female Participation in {sport}",
        color_discrete_map={"Female %": "pink", "Male %": "blue"}
    )

    fig.update_layout(
        barmode="relative",
        xaxis=dict(
            type="category",
            tickmode="array",
            tickvals=data["Year"],
            ticktext=data["Year"],
        ),
        yaxis=dict(title="percentage of participation"),
        plot_bgcolor="white"
    )

    fig.add_hline(y=50, line_dash="dash", line_color="black", annotation_text="50%",
                  annotation_position="right", annotation_font_size=14, annotation_font_color="black")

    fig.update_xaxes(tickangle=-90)

    return fig

def stacked_bar_chart_9(medal_counts):
    
    top_athletes = medal_counts.groupby("Name")["Count"].sum().nlargest(10)
    medal_counts = medal_counts[medal_counts["Name"].isin(top_athletes.index)]
    medal_colors = {"Gold": "#FFD700", "Silver": "#C0C0C0", "Bronze": "#CD7F32"}

    ordered_athletes = top_athletes.index[::-1]
    
    fig = px.bar(
        medal_counts,
        x="Count",
        y="Name",
        color="Medal",
        orientation="h",
        # title="Olympic Hall of Fame",
        labels={"Count": "Total Medals", "Name": "Athletes"},
        color_discrete_map=medal_colors,
        category_orders={"Name": ordered_athletes}
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Total Medals",
        yaxis_title="",
        showlegend=True
    )
    
    return fig