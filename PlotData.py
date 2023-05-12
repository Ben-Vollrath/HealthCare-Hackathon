
data = {
    'Montag': [['Abteilung 1', 10], ['Abteilung 2', 15], ['Abteilung 3', 5], ['Sonstiges', 7]],
    'Dienstag': [['Abteilung 5', 12], ['Abteilung 6', 14], ['Abteilung 7', 8], ['Sonstiges', 6]],
    'Mittwoch': [['Abteilung 9', 11], ['Abteilung 10', 13], ['Abteilung 11', 9], ['Sonstiges', 7]],
    'Donnerstag': [['Abteilung 13', 10], ['Abteilung 14', 16], ['Abteilung 15', 5], ['Sonstiges', 9]],
    'Freitag': [['Abteilung 17', 12], ['Abteilung 18', 15], ['Abteilung 19', 6], ['Sonstiges', 7]],
    'Samstag': [['Abteilung 21', 11], ['Abteilung 22', 14], ['Abteilung 23', 9], ['Sonstiges', 6]],
    'Sonntag': [['Abteilung 25', 10], ['Abteilung 26', 15], ['Abteilung 27', 8], ['Sonstiges', 7]]
}


import plotly.graph_objects as go

fig = go.Figure()

# Assume that every day has the same number of tasks
num_tasks_per_day = len(data['Montag'])

# Create stacked bar for each task
for i in range(num_tasks_per_day):
    fig.add_trace(go.Bar(
        x=list(data.keys()),
        y=[data[day][i][1] for day in data],
        name=data['Montag'][i][0],
        text=[data[day][i][0] for day in data],
        hoverinfo='text+y',
    ))

fig.update_layout(
    barmode='stack',
    title='Graphische Darstellung der Krankenfahrten',
    xaxis={'title': 'Wochen Tag'},
    yaxis={'title': 'Anzahl von Fahrten'},
    showlegend=False
)

fig.show()
