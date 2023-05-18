from InteractiveInterface import InteractiveInterface
from DataProcessing import DataProcessing
if __name__ == '__main__':
    dp = DataProcessing() # New DataProcesser Object

    InteractiveInterface = InteractiveInterface(dp) # New InteractiveInterface Object with the DataProcesser Object as parameter
    InteractiveInterface.run_interface(debug=True) # Run the Interface


