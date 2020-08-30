
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
        # timestampStr = datetime.now().strftime("%d-%b-%Y_%H_%M")
   
        if (not dev_mode) and (not os.path.exists(env_path)):
            os.mkdir(env_path)

        self.report_dir = f'-{dir_name}'
        self.dir_path = f'{env_path}-{dir_name}'
     
        if (not dev_mode) and (not os.path.exists(self.dir_path)):
            os.mkdir(self.dir_path)

    def gen_fig_tex(self, path, caption, label):

         with open(f'{self.dir_path}/fig_tex.txt', 'a+') as f:
                f.write("""
\\FloatBarrier
\\begin{figure}[!htb]
\\begin{center}
\\includegraphics[width=1\\textwidth]{%s}
\\caption{%s}
\\label{%s}
\\end{center}
\\end{figure}
\\FloatBarrier

""" % (
        path,
        caption,
        label,
    )) 

    def save_figure(self,config: dict, plot, name:str, ndir:str, typep:str='placeholder', legend:bool=True):
            

        if self.dev_mode:
            if legend:
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            plt.show()
            
        else:
            if not os.path.exists(f'{self.dir_path}/{ndir}'):
                os.mkdir(f'{self.dir_path}/{ndir}')

            name_no_colon = name.replace(':','')
            path = f'graphs/{self.report_dir}/{ndir}/{"_".join([typep]+name_no_colon.split())}.png'
            caption = name.replace('_','\\_')
            label = f'figure:{ndir}:{"_".join([typep]+name_no_colon.split())}'
            self.gen_fig_tex(path, caption, label)
            
            if legend:
                plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
                print(self.dir_path,ndir,typep,)

                plot.figure.savefig(f'{self.dir_path}/{ndir}/{"_".join([typep]+name_no_colon.split())}.png',bbox_inches='tight')
            else:
                plot.savefig(f'{self.dir_path}/{ndir}/{"_".join([typep]+name_no_colon.split())}.png')
        
        plt.clf()
    
    def save_table(self,df, description, ndir):
        if self.dev_mode:
            print(df.to_latex(index=False))
            print(df)
        else:
            with open(f'{self.dir_path}/{ndir}-tables.txt', 'a+') as f:
                f.write(f'\n -- New table --\n')
                f.write(f'\n{description}\n')
                f.write(df.to_latex(index=False))
                f.write('\n')

    

    #########################
    ##  Graphs and plots  ##
    ########################


    # --> Relational plots <--
    def line_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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
                    markers= config['markers'] if 'markers' in config else None,
                    data= data)
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name,size=h_size)

    
        # self.save_figure(config,plot,name,f'{self.dir_path}/{ndir}')
        self.save_figure(config,plot,name,ndir,'lineplot')
    
    def scatter_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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
                    markers= config['markers'] if 'markers' in config else None,
                    alpha= config['alpha'] if 'alpha' in config else None,
                    data= data)
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name,size=h_size)

    
        self.save_figure(config,plot,name,ndir,'scatterplot')
    

    def rel_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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
                    markers= config['markers'] if 'markers' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size= h_size)

        self.save_figure(config,plot,name,ndir,'relplot',legend=False)
    

    ###########################
    # --> Categorial plots <--#
    ###########################
    
    def cat_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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
                    height= config['height'] if 'height' in config else 5,
                    aspect= config['aspect'] if 'aspect' in config else 1,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    markers= config['markers'] if 'markers' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        # plt.title(name, size=h_size)

        self.save_figure(config, plot,name, ndir, 'catplot', legend=False)
    
    def strip_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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
                    alpha= config['alpha'] if 'alpha' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name,ndir,'stripplot')

    def swarm_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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

        self.save_figure(config,plot,name,ndir,'swarmplot')
    

    def box_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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
        if 'strip' in config:
            sns.stripplot(x=config['x_strip'], y=config['y_strip'], color='black',
                size=10, alpha=0.3, data=data)
        
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name,ndir,'boxplot')

    
    def violin_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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
                    markers= config['markers'] if 'markers' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name, ndir, 'violinplot')
    

    def boxen_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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

        self.save_figure(config,plot,name,ndir,'boxenplot')
    

    def point_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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
                    markers= config['markers'] if 'markers' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name,ndir, 'pointplot')
    

    def bar_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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

        self.save_figure(config,plot,name,ndir, 'barplot')
    

    def count_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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

        self.save_figure(config,plot,name,ndir,'countplot')
    

    #############################
    # --> Distibrution plots <--#
    #############################
    
    def dist_plot(self, data:list, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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

        self.save_figure(config,plot,name,ndir,'distplot')
    

    def rug_plot(self, data:list, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.figure(5)
        plot = sns.rugplot(a= data,
                        axis='x' if 'x' in config else 'y',
                        height= config['height'] if 'height' in config else None,
                        color= config['color'] if 'color' in config else None,
                        )
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        plt.title(name, size=h_size)

        self.save_figure(config,plot,name,ndir, 'rugplot')
    
    
    #############################
    # --> Regression plots <--  #
    #############################

    def lm_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.figure(5)
        plot = sns.lmplot(x=config['x'],
                    y= config['y'],
                    hue= config['hue'] if 'hue' in config else None,
                    fit_reg= False if 'fit_reg' in config else True,
                    scatter= False if 'scatter' in config else True,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    markers= config['markers'] if 'markers' in config else None,
                    height= config['height'] if 'height' in config else 5,
                    aspect= config['aspect'] if 'aspect' in config else 1,
                    col= config['col'] if 'col' in config else None,
                    row= config['row'] if 'row' in config else None,
                    x_jitter= config['x_jitter'] if 'x_jitter' in config else None,
                    y_jitter= config['y_jitter'] if 'y_jitter' in config else None,
                    line_kws= config['line_kws'] if 'line_kws' in config else None,
                    data= data)
        
        if 'row' not in config and 'col' not in config:
            if 'xlabel' in config:
                plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
            if 'ylabel' in config:
                plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        
            plt.title(name, size=h_size)

        self.save_figure(config,plot,name,ndir, 'lmplot',legend=False)
        
    #############################
    # --> Multi plots <--  #
    #############################

    def joint_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.figure(5)
        plot = sns.jointplot(x=config['x'],
                    y= config['y'],
                    kind= config['kind'],
                    dropna= True if 'dropna' in config else False,
                    color= config['color'] if 'color' in config else None,
                    height= config['height'] if 'height' in config else 5,
                    # line_kws= config['line_kws'] if 'line_kws' in config else None,
                    data= data)
        
        if 'xlabel' in config:
            plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        if 'ylabel' in config:
            plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])


        self.save_figure(config,plot,name,ndir,'jointplot',legend=False)
    

    def pair_plot(self, data, config:dict, name:str, ndir:str, h_size=20):
        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
        if 'meta_style' in config:
            sns.set(style=config['meta_style'], 
                    color_codes= True if 'color_codes' in config else False)
        else:
            sns.set(style= "darkgrid", 
                    color_codes= True)
        plt.figure(5)
        plot = sns.pairplot(hue= config['hue'] if 'hue' in config else None,
                    palette= config['palette'] if 'palette' in config else None,
                    hue_order= config['hue_order'] if 'hue_order' in config else None,
                    kind= config['kind'],
                    markers= config['markers'] if 'markers' in config else None,
                    height= config['height'] if 'height' in config else 5,
                    aspect= config['aspect'] if 'aspect' in config else 1,
                    vars= config['vars'] if 'vars' in config else None,
                    x_vars= config['x_vars'] if 'x_vars' in config else None,
                    y_vars= config['y_vars'] if 'y_vars' in config else None,
                    dropna= True if 'dropna' in config else False,
                    # line_kws= config['line_kws'] if 'line_kws' in config else None,
                    data= data)
        
        # if 'xlabel' in config:
        #     plt.xlabel(config['xlabel'][0], size=config['xlabel'][1])
        # if 'ylabel' in config:
        #     plt.ylabel(config['ylabel'][0], size=config['ylabel'][1])

        # plt.title(name, size=h_size)
        
        self.save_figure(config,plot,name,ndir,'pairplot',legend=False)
    
    
    # overlay plots by giving list of lambda's

    def dynamic_multi_plot(self, 
                            data, 
                            config:dict, 
                            name:str, 
                            ndir:str, 
                            plots:list,
                            h_size=20,
                            ):

        # if (not self.dev_mode) and (not os.path.exists(f'{self.dir_path}/{ndir}')):
        #     os.mkdir(f'{self.dir_path}/{ndir}')
        
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

    
        self.save_figure(config,plot,name,ndir,'dynamicplot')
        
    
    
        

        
        
        
        
        

        

        