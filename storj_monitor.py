import os
import shutil
from time import sleep
import time
import datetime as dt
import pandas as pd
import argparse


#%%

node1_exe_file = os.path.join(r'C:\Program Files\Storj\Storage Node', 'storagenode.exe')
def node1_stop(self):
    os.system('powershell.exe Stop-Service storagenode')
def node1_start(self):
    os.system('powershell.exe Start-Service storagenode')
def node1_restart(self):
    os.system('powershell.exe Restart-Service storagenode')
def get_node1_exe_size():
    return os.path.getsize(node1_exe_file)


class Node:
    
    def __init__(self, node_number, dt_start_stop=60, dt_check_log=30, n_lines_log_check=5, verbose=False):
        
        self.node_number = node_number
        self.dt_start_stop = dt_start_stop
        self.dt_check_log = dt_check_log
        self.n_lines_log_check = n_lines_log_check
        self.verbose = verbose
        
        # Define main directory
        if self.node_number == 1:
            self.directory = r'C:\Program Files\Storj\Storage Node'
            self.node_id = 'storagenode'
        else:
            self.directory = fr'C:\Program Files\Storj{self.node_number - 1}\Storage Node'
            self.node_id = f'storagenode{node_number - 1}'
            
        self.exe_file = os.path.join(self.directory, 'storagenode.exe')
        self.log_file = os.path.join(self.directory, 'storagenode.log')
            
                
    # Start, Stop, Restart Node
    def stop(self):
        os.system(f'powershell.exe Stop-Service {self.node_id}')
    def start(self):
        os.system(f'powershell.exe Start-Service {self.node_id}')
    def restart(self):
        os.system(f'powershell.exe Restart-Service {self.node_id}')
    
    
    # Check/Replace .exe
    def replace_exe(self):
        if self.verbose:
            print(f'\tChecking .exe size...')
        node1_exe_size = round(get_node1_exe_size() / 1048576, 2)
        self.exe_size = round(os.path.getsize(self.exe_file) / 1048576, 2)
        checks.loc[self.node_number, '.exe Size'] = self.exe_size
        
        if self.exe_size != node1_exe_size:
            if self.verbose:
                print(f'\t\t.exe size does not match with Node 1: {self.exe_size} vs. {node1_exe_size}')
                print(f'\t\tReplacing Node {self.node_number} .exe with Node 1...')
            # node1_stop()
            self.stop()
            sleep(self.dt_start_stop)
            os.system(f'copy \"{node1_exe_file}\" \"{self.node_exe_filename}\" /Y')
            sleep(self.dt_start_stop)
            # node1_start()
            self.start()
            checks.log[self.node_number, '.exe Updated'] += 1
        elif self.verbose:
            print('\t\t.exe sizes are consistent.')
    
    
    # Check/replace .log
    def log_status(self, verbose=False):
        
        # Check if the last 5 lines of the log are the same after some time
        if self.verbose:
            print(f'\tChecking if .log has frozen...')
        with open(self.log_file, 'r+') as log:
            lines_init = log.readlines()[-self.n_lines_log_check:]
            if self.verbose:
                print(f'\t\tChecking last {self.n_lines_log_check} lines of {self.log_file}...')
                
        if self.verbose:
            wait = self.dt_check_log
            print('\t\tWaiting...')
            while wait > 0:
                print(f'\t\t\t{wait} ', end='\r')
                sleep(1)
                wait -= 1
        else:
            sleep(self.dt_check_log)
        
        with open(self.log_file, 'r+') as log:
            lines_final = log.readlines()[-self.n_lines_log_check:]
            if self.verbose:
                print(f'\t\tChecking last {self.n_lines_log_check} lines of {self.log_file} again...')
        matches = [line_init == line_final for line_init, line_final in zip(lines_init, lines_final)]
        
        if any(matches):
            if self.verbose:
                print('\t\tLine(s) match. Assuming node is stuck. Restarting...')
            checks.loc[self.node_number, '.log Frozen'] += 1
            self.restart()
        elif self.verbose:
            print(f'\t\tLast {self.n_lines_log_check} lines changed. Assuming log status good.')
        
        
        # Check the log size
        if self.verbose:
            print(f'\tChecking .log size for Node {self.node_number}...')
        self.log_size = round(os.path.getsize(self.log_file) / 1048576, 2) # MB
        checks.loc[self.node_number, '.log Size'] = self.log_size
        if self.log_size > 2000:
            if self.verbose:
                print(f'\t\t{self.log_size} MB. Too big, renaming and creating new one...')
            log_file_old = self.log_file.replace('.log', f'{dt.date.today()}.log')
            self.stop()
            os.rename(self.log_file, log_file_old)
            open(self.log_file, 'a').close()
            self.start()
            checks.loc[self.node_number, '.log Too Big'] += 1
        elif self.verbose:
            print(f'\t\t{self.log_size} MB. Small enough, will not replace.')
            
            
#%%

# verbose = False
# dt_loop = 10 * 60 # 10 minutes between loops

# checks = pd.DataFrame(index=[1, 2, 3, 4, 5], columns=['.exe Size', '.log Size', '.log Frozen', '.log Too Big', '.exe Updated', 'Checks'])
# checks.fillna(0, inplace=True)

# node1 = Node(node_number=1, verbose=verbose)
# node2 = Node(node_number=2, verbose=verbose)
# node3 = Node(node_number=3, verbose=verbose)
# node4 = Node(node_number=4, verbose=verbose)
# node5 = Node(node_number=5, verbose=verbose)

# loops = 0
# print('#' * 50)
# while True:
#     if verbose:
#         print(f'############### Loop {loops} ###############')
    
#     for num, node in enumerate([node1, node2, node3, node4, node5]):
#         num += 1
#         if verbose:
#             print(f'Node {num}')
        
#         node.log_status() # Check .log
#         node.replace_exe() # Check .exe
        
#         checks.loc[num, 'Checks'] += 1
    
#     if verbose:
#         print('##########')
#     print(checks)
#     print('##########')
    
#     loops += 1
    
#     wait = dt_loop
#     while wait > 0:
#         print(f'Waiting: {wait}', end='\r')
#         sleep(1)
#         wait -= 1
        
#     print('#' * 50)
        
    # break


#%%

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Storj Node Monitor')
    
    parser.add_argument('-n', '--n_nodes', type=int, help='Number of Nodes', default=5)
    parser.add_argument('-v', '--verbose', help='Verbose', action='store_true')
    parser.add_argument('-l', '--dt_loop', type=int, help='Time (seconds) between loops', default=600)
    
    args = parser.parse_args()
    n_nodes = args.n_nodes
    verbose = args.verbose
    dt_loop = args.dt_loop
    
    ###
    
    checks = pd.DataFrame(index=[1, 2, 3, 4, 5], columns=['.exe Size', '.log Size', '.log Frozen', '.log Too Big', '.exe Updated', 'Checks'])
    checks.fillna(0, inplace=True)
    
    nodes = [Node(node_number=i+1, verbose=verbose) for i in range(n_nodes)]
    
    ###
    
    loops = 0
    print('#' * 50)
    while True:
        if verbose:
            print(f'############### Loop {loops} ###############')
        
        for num, node in enumerate(nodes):
            num += 1
            if verbose:
                print(f'Node {num}')
            
            node.log_status() # Check .log
            node.replace_exe() # Check .exe
            
            checks.loc[num, 'Checks'] += 1
        
        if verbose:
            print('##########')
        print(checks)
        print('##########')
        
        loops += 1
        
        wait = dt_loop
        while wait > 0:
            print(f'Waiting: {wait} ', end='\r')
            sleep(1)
            wait -= 1
            
        print('#' * 50)
    
        

