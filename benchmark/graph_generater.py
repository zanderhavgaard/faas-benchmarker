
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
from datetime import datetime

# default context values for dark grid
# {'font.size': 12.0, 
# 'axes.labelsize': 12.0, 
# 'axes.titlesize': 12.0, 
# 'xtick.labelsize': 11.0, 
# 'ytick.labelsize': 11.0, 
# 'legend.fontsize': 11.0, 
# 'axes.linewidth': 1.25, 
# 'grid.linewidth': 1.0, 
# 'lines.linewidth': 1.5, 
# 'lines.markersize': 6.0, 
# 'patch.linewidth': 1.0, 
# 'xtick.major.width': 1.25, 
# 'ytick.major.width': 1.25, 
# 'xtick.minor.width': 1.0, 
# 'ytick.minor.width': 1.0, 
# 'xtick.major.size': 6.0, 
# 'ytick.major.size': 6.0, 
# 'xtick.minor.size': 4.0, 
# 'ytick.minor.size': 4.0, 
# 'legend.title_fontsize': 12.0}

class GraphGenerater():
    
    def __init__(self, dir_name: str, dev_mode:bool=False):
        self.dev_mode = dev_mode
        env_path = os.getenv('fbrd') + '/graphs'
        timestampStr = datetime.now().strftime("%d-%b-%Y_(%H:%M:%S)")
   
        if not os.path.exists(env_path):
            os.mkdir(env_path)

        self.dir_path = f'{env_path}/{timestampStr}-{dir_name}'
     
        if not os.path.exists(self.dir_path):
            os.mkdir(self.dir_path)
        

    



    def save_figure(self,config: dict, name:str, plot):
       
        if self.dev_mode:
            plt.show()
        else:
            plot.figure.savefig(f'{self.dir_path}/{name}.png')

    
    def lineplot_graph(self, data, config:dict, name:str):
        
        if 'meta_style' in config:
            print('setting style',config['meta_style'])
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        # print('color_palette',sns.color_palette())
        print(sns.plotting_context())
    
        plot = sns.lineplot(x=config['x'],
                    y= config['y'],
                    hue= config['hue'] if 'hue' in config else None,
                    style= config['style'] if 'style' in config else None,
                    markers= True if 'markers' in config else False,
                    dashes= True if 'dashes' in config else False,
                    data= data)
    
        self.save_figure(config, name, plot)
        
        

        
        
        
        
        

        

        