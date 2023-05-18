
#Imports needed for the interactive interface
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State

import DataProcessing as DataProcesser
from GraphPlot import GraphPlot




#Class for the interactive interface using Dash
class InteractiveInterface:

    #Constructor
    def __init__(self,Dataprocesser):
        self.app = dash.Dash(__name__)
        self.dp = Dataprocesser
        #On object creation, create the layout and the callbacks
        self.create_layout() 
        self.create_callbacks()

    #app = dash.Dash(__name__) # Create the Dash app
    #dp  = DataProcesser() # Create the DataProcesser object
    
    def create_layout(self):
        """Create the layout of the Dash app
        """
        self.app.layout = html.Div([
        html.H1('Interface zu Darstellung von Krankenfahrten', style={'textAlign': 'center', 'color': '#4B0082'}), # Create the title
        dcc.Graph(id='graph', style={'height': '70vh', 'width': '80vw', 'margin': 'auto'}), # Create the graph
        html.Div([
            html.Label('Start Date', style={'padding': '10px', 'color': '#4B0082'}), # Label for the start date
            dcc.Input(id='start-date', type='text', value='', style={'width': '150px'}), # Input field for the start date
            html.Label('End Date', style={'padding': '10px', 'color': '#4B0082'}), # Label for the end date
            dcc.Input(id='end-date', type='text', value='', style={'width': '150px'}), # Input field for the end date
            html.Label('Hospital ID', style={'padding': '10px', 'color': '#4B0082'}), # Label for the hospital id
            dcc.Input(id='hospital-id', type='text', value='', style={'width': '150px'}), # Input field for the hospital id
            html.Button('Update Graph', id='update-button', n_clicks=0, style={ # Button to update the graph
                'background-color': '#4B0082', 'color': 'white', 'border': 'none', 'padding': '10px 20px',
                'text-align': 'center', 'text-decoration': 'none', 'display': 'inline-block', 'font-size': '16px',
                'margin': '4px 2px', 'cursor': 'pointer', 'border-radius': '12px'
            }),
        ], style={ # Style for the div containing the input fields and the button
            'display': 'flex',
            'justifyContent': 'space-around',
            'padding': '20px'
        }),
        ], style={'backgroundColor': '#E6E6FA', 'padding': '20px'}) # Style for the whole layout


    def create_callbacks(self):
        @self.app.callback(
            Output('graph', 'figure'), # Output is the graph
            [Input('update-button', 'n_clicks'), # This button is used to update the graph
            Input('graph', 'clickData')],  # This is used to get the clicked data point in order to zoom into that day
            [State('start-date', 'value'), # These are the input fields
            State('end-date', 'value'), # These are the input fields
            State('hospital-id', 'value')] # These are the input fields
        )
        def update_graph(n_clicks, clickData, start_date, end_date, hospital_id):
            """Function used to Update the Graph, is triggered on every input change

            Args:
                n_clicks (_type_): The amount of clicks on the Update Button
                clickData (_type_): The data of the clicked data point, used to zoom into that day
                start_date (_type_): The start date of the time period (filter)
                end_date (_type_): The end date of the time period (filter)
                hospital_id (_type_): The id of the hospital (filter)

            Returns:
                Returns the plot of the graph
            """

            changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0] #Go through changes
            if 'update-button' in changed_id: # If the button has been clicked
                if n_clicks > 0:
                    #If update button is clicked we update the week graph
                    sum_list = [0] * 7
                    r = self.dp.sendRequest(start_date, end_date)

                    #Filter the data if a hospital id is given
                    if(hospital_id != ''):
                        r = self.dp.filterData(r, 'hospitalId', hospital_id)


                    sum_list = self.dp.getDataOfWeek(r)
                    return GraphPlot.plotStackedBarChartWeek(sum_list)

            elif 'graph' in changed_id:
                if clickData:
                    #If Graph is clicked we update the day graph
                    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
                    day = weekdays.index(clickData['points'][0]['x'])

                    r = self.dp.sendRequest(start_date, end_date)

                    #Filter the data if a hospital id is given
                    if(hospital_id != ''):
                        r = self.dp.filterData(r, 'hospitalId', hospital_id)


                    dayData = self.dp.getDataOfDay(r, day)
                    return GraphPlot.plotStackedBarChartDay(dayData,clickData['points'][0]['x'])

            # If the button hasn't been clicked, return an empty figure
            return GraphPlot.plotEmpty()
        
    def run_interface(self,debug):
        """Run the Dash app

        Args:
            debug (_type_): If debug is true, the app will be run in debug mode
        """
        self.app.run_server(debug=debug) # Run the Dash app


    
