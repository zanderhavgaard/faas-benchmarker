
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

class GraphGenerater():
    
    def __init__(self, path: str):
        self.path = path
    
    def lineplot_graph(self, data:dataframe, config:dict = None):
        if config != None and style in config:
            sns.set(style=config['style'])
        else:
            sns.set(style="darkgrid")
        
        
        

        

        