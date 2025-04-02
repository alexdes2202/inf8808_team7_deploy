from preprocess import preprocess_sankey_data
import plotly.graph_objects as go

from theme import GOLD, SILVER, BRONZE, NO_MEDAL
import hover_template

# Function to create the Sankey plot for a given year or for all editions
def create_sankey_plot(olympics_data, year, sport, selected_country, is_relative = False):

    df_medals, medal_counts = preprocess_sankey_data(olympics_data, year, sport, selected_country)
    
    if df_medals is None:
      return None

    # List of nodes for Sankey
    countries = medal_counts['NOC'].unique().tolist()

    # Add the nodes "Medal" and "No Medal" for each country
    all_labels = countries + [f'{medal}_{country}' for country in countries for medal in ['Gold', 'Silver', 'Bronze', 'No Medal']]

    # Indices mapping
    source_indices = []
    target_indices = []
    values = []

    medal_order = ['Gold', 'Silver', 'Bronze', 'No Medal']

    for country in countries:
        # Count the total number of medals
        medal_count = df_medals[(df_medals['NOC'] == country) & (df_medals['Medal'] != 'No Medal')].shape[0]

        medal_values = {medal: 0 for medal in medal_order}

        # Link each country and its medals
        for medal in ['Gold', 'Silver', 'Bronze']:

            medal_NOC = f'{medal}_{country}'

            if is_relative == False:
              count = medal_counts[(medal_counts['Medal_NOC'] == medal_NOC)]['Count'].sum()
            else:
              count = medal_counts[(medal_counts['Medal_NOC'] == medal_NOC)]['Percentage'].sum()
              medal_values[medal] = count

            # if count > 0:
            if True: 
                source_indices.append(all_labels.index(country))
                target_indices.append(all_labels.index(medal_NOC))
                values.append(count)

        if is_relative == False:
          no_medal_count = len(df_medals[df_medals['NOC'] == country]) - medal_count
        else:
          no_medal_count = 100 - sum(medal_values.values())

        # Add the link for 'No Medal'
        # if no_medal_count > 0:
        if True:
            no_medal_NOC = f'No Medal_{country}'
            source_indices.append(all_labels.index(country))
            target_indices.append(all_labels.index(no_medal_NOC))
            values.append(no_medal_count)

    medal_colors = {
        'Gold': GOLD, 
        'Silver': SILVER,
        'Bronze': BRONZE, 
        'No Medal': NO_MEDAL
    }

    # Add countries' colors
    node_colors = ['black'] * len(countries)
    for idx, label in enumerate(countries):
      if label == selected_country:
          node_colors[idx] = 'red'

    # Add medals' colors
    for label in all_labels:
        if 'Gold' in label:
            node_colors.append(medal_colors['Gold'])
        elif 'Silver' in label:
            node_colors.append(medal_colors['Silver'])
        elif 'Bronze' in label:
            node_colors.append(medal_colors['Bronze'])
        elif 'No Medal' in label:
            node_colors.append(medal_colors['No Medal'])


    # Generate x and y for the nodes based on the same order of source and target indices
    if is_relative == False:
      # y_values = [0, 0, 0, 0, 0.05, 0.20, 0.35, 0.5, 0.6, 0.75, 0.9, 1.10, 1.15, 1.30, 1.45, 1.8, 2, 2.15, 2.3, 2.5]
      y_values = [0, 0, 0, 0, 0.05, 0.20, 0.35, 0.5, 0.6, 0.75, 0.9, 1.10, 1.15, 1.30, 1.45, 1.8, 2, 2.15, 2.3, 2.5]
      x_values = [0, 1, 2, 3, 0.35, 0.35, 0.35, 0.35, 0.351, 0.351, 0.351, 0.351, 0.352, 0.352, 0.352, 0.352, 0.353, 0.353, 0.353, 0.353]
    else:
      y_values = [0, 0, 0, 0, 0.05, 0.20, 0.35, 0.5, 0.6, 0.75, 0.9, 1.10, 1.15, 1.30, 1.45, 1.9, 2, 2.15, 2.3, 2.6]
      x_values = [0, 1, 2, 3, 0.35, 0.35, 0.35, 0.35, 0.351, 0.351, 0.351, 0.351, 0.352, 0.352, 0.352, 0.352, 0.353, 0.353, 0.353, 0.353]

    link_colors = []
    for idx,color in enumerate(node_colors[len(countries):]):
      # if values[idx] != 0:
      rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
      link_colors.append(f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.7)")
    
    # Sankey Diagram
    fig = go.Figure(go.Sankey(
        orientation = 'v',
        arrangement = "snap",
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            # x=x_values,
            # y=y_values,
            label=countries,
            color=node_colors,
            customdata=countries + [country for country in countries for _ in range(4)],
            hovertemplate=hover_template.source_sankey_hover(is_relative)
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color=link_colors,
            line=dict(color="grey", width=0.3),
            customdata=[(label.split('_')[0], label.split('_')[1]) for label in all_labels if label not in countries],
            hovertemplate=hover_template.performance_sankey_hover(is_relative)
        )
    ))

    # Relative/Absolute Mode
    if is_relative == False:
      plot_type = 'Count'
    else :
      plot_type = 'Percentage'
    fig.update_layout(
        title_text=f'Medal distribution in {sport} by {plot_type} (Edition : {year})',
        font_size=12
    )

    # return fig , source_indices, target_indices, values
    return fig