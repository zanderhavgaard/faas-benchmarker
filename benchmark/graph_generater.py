
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
from datetime import datetime
from pprint import pprint
from warnings import filterwarnings 

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
        timestampStr = datetime.now().strftime("%d-%b-%Y_(%H:%M)")
   
        if (not dev_mode) and (not os.path.exists(env_path)):
            os.mkdir(env_path)

        self.dir_path = f'{env_path}/{timestampStr}-{dir_name}'
     
        if (not dev_mode) and (not os.path.exists(self.dir_path)):
            os.mkdir(self.dir_path)
        

    def save_figure(self,config: dict, plot, name:str, path:str, legend:bool=True):
        if self.dev_mode:
            if legend:
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            plt.show()
            
        else:
            if legend:
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                plot.figure.savefig(f'{path}/{name}.png',bbox_inches='tight')
            else:
                plot.savefig(f'{path}/{name}.png')
        
        plt.clf()

    

    #########################
    ##  Graphs and plots  ##
    ########################


    # --> Relational plots <--
    def lineplot_graph(self, data, config:dict, name:str, ndir:str, h_size=20):
        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        
     
        plt.figure(1)
        plot = sns.lineplot(x=config['x'],
                    y= config['y'],
                    hue= config['hue'] if 'hue' in config else None,
                    style= config['style'] if 'style' in config else None,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    data= data)
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name,size=h_size)

    
        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}')
    
    def scatter_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        
     
        plt.figure(2)
        plot = sns.scatterplot(x=config['x'],
                    y= config['y'],
                    hue= config['hue'] if 'hue' in config else None,
                    style= config['style'] if 'style' in config else None,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    data= data)
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name,size=h_size)

    
        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}')
    

    def relplot(self, data, config:dict, name:str, ndir:str, h_size=20):
        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.clf()
        plot = sns.relplot(x=config['x'],
                    y= config['y'],
                    hue= config['hue'] if 'hue' in config else None,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size= h_size)

        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}',legend=False)
    

    ###########################
    # --> Categorial plots <--#
    ###########################
    def cat_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.figure(3)
        # plt.clf()
        plot = sns.catplot(x=config['x'],
                    y= config['y'],
                    row= config['row'] if 'row' in config else None,
                    col= config['col'] if 'col' in config else None,
                    hue= config['hue'] if 'hue' in config else None,
                    kind= config['kind'] if 'kind' in config else 'strip',
                    jitter= config['jitter'] if 'jitter' in config else False,
                    height= config['height'] if 'height' in config else 4,
                    aspect= config['aspect'] if 'aspect' in config else 1.5,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        # plt.title(name, size=h_size)

        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}', legend=False)
    
    def strip_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        # plt.figure(4)
        plt.clf()
        plot = sns.stripplot(x=config['x'],
                    y= config['y'],
                    hue= config['hue'] if 'hue' in config else None,
                    palette= config['palette'] if 'palette' in config else None,
                    jitter= config['jitter'] if 'jitter' in config else False,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}')

    def swarm_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.figure(5)
        plot = sns.swarmplot(x=config['x'],
                    y= config['y'],
                    hue= config['hue'] if 'hue' in config else None,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}')
    

    def box_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.figure(6)
        plot = sns.boxplot(x=config['x'],
                    y= config['y'],
                    hue= config['hue'] if 'hue' in config else None,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}')

    
    def violin_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.figure(5)
        plot = sns.violinplot(x=config['x'],
                    y= config['y'],
                    hue= config['hue'] if 'hue' in config else None,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}')
    

    def boxen_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.figure(5)
        plot = sns.boxenplot(x=config['x'],
                    y= config['y'],
                    hue= config['hue'] if 'hue' in config else None,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}')
    

    def point_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.figure(5)
        plot = sns.pointplot(x=config['x'],
                    y= config['y'],
                    hue= config['hue'] if 'hue' in config else None,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}')
    

    def bar_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.figure(5)
        plot = sns.barplot(x=config['x'],
                    y= config['y'],
                    hue= config['hue'] if 'hue' in config else None,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}')
    

    def count_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.figure(5)
        plot = sns.countplot(x=config['x'] if 'x' in config else None,
                    y= config['y'] if 'y' in config else None,
                    hue= config['hue'] if 'hue' in config else None,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}')
    

    ###########################
    # --> Distibrution plots <--#
    ###########################
    
    def dist_plot(self, data:list, config:dict, name:str, ndir:str, h_size=20):
        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.figure(5)
        plot = sns.distplot(a= data,
                        hist=config['hist'],
                        kde= config['kde'],
                        color= config['color'] if 'color' in config else None,
                        bins= config['bins'] if 'bins' in config else None)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}')
    
    
        
    # overlay plots by giving list of lambda's

    def dynamic_multi_plot(self, 
                            data, 
                            config:dict, 
                            name:str, 
                            ndir:str, 
                            plots:list,
                            h_size=20,
                            ):

        if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
            os.mkdir(f'{self.dir_path}/{ndir}')
        
        meta_style = config.pop('meta_style') if 'meta_style' in config else None
        if meta_style != None:
            sns.set(style=meta_style, 
                    color_codes= True)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        
        xlabel = config.pop('xlabel') if 'xlabel' in config else None
        ylabel = config.pop('ylabel') if 'ylabel' in config else None

        args = list(config.values())+[data]
       
     
        plt.figure(99)
        for xlambda in plots:
            plot = xlambda(args)

        if xlabel != None:
            plt.xlabel(xlabel[0], size=xlabel[1])
        if ylabel != None:
            plt.ylabel(ylabel[0], size=ylabel[1])

        plt.title(name,size=h_size)

    
        self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}')
        
        

        
        
        
        
        

        

        