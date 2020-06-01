import sys
import os
import pathlib
fbrd = os.getenv('fbrd')
exp_path = pathlib.Path(f'{fbrd}/experiments')
[sys.path.insert(1,str(exp)) for exp in exp_path.iterdir() if exp.is_dir()]

