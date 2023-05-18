import plotly.express as px
import plotly.graph_objects as go

class GraphPlot:
    @staticmethod
    def plotStackedBarChartDay(data, selected_day):
        """Creates a stacked bar chart for the given data of a day

        Args:
            data (_type_): The INPUT data to be processed
            selected_day (_type_): The selected day

        Returns:
            _type_: Returns the Graph with x hours of day and y amount of transports
        """
        fig = go.Figure()

        num_tasks_per_hour = len(data[0])
        hours = [str(i) for i in range(24)]  # The 24 hours of a day

        colors = px.colors.qualitative.Pastel2  # use the Plotly color palette

        for i in range(num_tasks_per_hour):
            fig.add_trace(go.Bar(
                x=hours,
                y=[data[hour][i][1] for hour in data],
                name=data[0][i][0],
                text=[data[hour][i][0] for hour in data],
                hoverinfo='text+y',
                marker=dict(color=colors[i % len(colors)]),  # set the color of the bar
                textfont=dict(size=16),  # set the size of the text inside the bars
            ))

        fig.update_layout(
            barmode='stack',
            title=f'Graphische Darstellung der Krankenfahrten am {selected_day}',
            xaxis={'title': 'Stunden des Tages', 'titlefont': {'size': 18}},  # set the size of the x-axis title
            yaxis={'title': 'Anzahl von Fahrten', 'titlefont': {'size': 18}},  # set the size of the y-axis title
            showlegend=False
        )

        return fig
    @staticmethod
    def plotStackedBarChartWeek(data):
        """Creates a stacked bar chart for the given data of a week

        Args:
            data (_type_): The INPUT data to be processed

        Returns:
            _type_:  Returns the Graph with x weekdays of day and y amount of transports
        """
        fig = go.Figure()

        num_tasks_per_day = len(data[0])
        weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

        colors = px.colors.qualitative.Pastel2 # use the Plotly color palette

        for i in range(num_tasks_per_day):
            fig.add_trace(go.Bar(
                x=weekdays,
                y=[data[day][i][1] for day in data],
                name=data[0][i][0],
                text=[data[day][i][0] for day in data],
                hoverinfo='text+y',
                marker=dict(color=colors[i % len(colors)]), # set the color of the bar
                textfont=dict(size=16), # set the size of the text inside the bars
            ))

        fig.update_layout(
            barmode='stack',
            title='Graphische Darstellung der Krankenfahrten',
            xaxis={'title': 'Wochen Tag', 'titlefont': {'size': 18}}, # set the size of the x-axis title
            yaxis={'title': 'Anzahl von Fahrten', 'titlefont': {'size': 18}}, # set the size of the y-axis title
            showlegend=False
        )

        return fig

    @staticmethod
    def plotEmpty():
        """Creates an empty Graph

        Returns:
            _type_: Returns the Graph
        """
        # Create empty figure
        return go.Figure()