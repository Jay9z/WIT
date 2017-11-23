# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 10:01:34 2017

@author: COMAC
"""
#import sys
import re
import pandas as pd
import numpy as np
class pgv:
    # line: command,addr_a,pin_a,addr_b,status,value,unit,pin_b
    def __init__(self,file_in,prog_out,report_out):
        '''
        '''
        self._file_in = file_in
        self._prog_out = prog_out
        self._report_out = report_out
        self._lists = pd.DataFrame([],columns=["command","addr_a","pin_a","addr_b","status","value","unit","pin_b"])
        self._stats = {} 

    def analysis(self):   
        '''
        '''
        self._lists_from_log()
        self._count()
        self._ratio()
        
    def prog_out(self):
        '''
        
        '''
#        if (not self._lists):
#            print("No data found!")
#            return
        #print(self._lists)    
        high_line = self._lists[self._lists["status"]=="HIGH"]
        pin_ab = high_line.filter(items=["pin_a","pin_b"])
        with pd.ExcelWriter(self._prog_out) as writer:
            pin_ab.to_Excel(writer,sheet_name='retesting',index=False)
    
    def report_out(self,thr= 0.5):
        '''
        print out
        '''
        lst=self._stats_sort(threshold=0.5)          
        str_line = "===Node Name===HIGH Ratio===\n" 
        for item in lst:
            connector,passratio = item[0],item[1][2]
            str_line += "%12s%10.2f%%\n"%(connector,passratio*100)
            
        with open(self._report_out,'w') as fp:    
            fp.write(str_line)
           
        
    def _lists_from_log(self):
        '''
        In -- TXT file of testing report
        Return -- [[ ],...]
        '''
        fp = open(self._file_in,U'r')
        i = 0
        lists =[]
        for line in fp:
            info = line.split()
            if info and info[0]==':':
                if i%2==0:
                    lists.append(info[1:])
                else:
                    lists[i/2].extend(info[1:])
                i += 1;
        fp.close()
        self._lists = pd.DataFrame(lists,columns=["command","addr_a","pin_a","addr_b","status","value","unit","pin_b"])   
        
    def _connector(self,pin_name):
        '''
        In -- pin name
        Return -- Connector name
        '''
        re1 = re.compile("[0-9A-Z]+-[0-9A-Z]+-[0-9A-Z]+")
        mt = re1.search(pin_name)
        if mt:
            return mt.group(0)
        else:
            return pin_name    
     
    def _count(self):
        '''
        {'Connector Name':(PASS number,HIGH number,PASS ratio)}
        '''
        result = dict()
        row,col = self._lists.shape
        for i in range(row):
            info = self._lists.iloc[i]
            #print("info:",info)
            status,pin_a,pin_b = info[4],info[1],info[7]
            connector_a ,connector_b = self._connector(pin_a),self._connector(pin_b)
            valueA = result.get(connector_a,(0,0,0))
            valueB = result.get(connector_b,(0,0,0))
            if status == 'PASS':
                result[connector_a] = (valueA[0]+1,valueA[1],0)
                result[connector_b] = (valueB[0]+1,valueB[1],0)
            elif status =='HIGH':
                result[connector_a] = (valueA[0],valueA[1]+1,0)
                result[connector_b] = (valueB[0],valueB[1]+1,0)
        self._stats = result
        
    def _ratio(self):
        '''
        calculate the ratio of HIGH result
        In -- {Node:(PASS number,HIGH number)}
        Return -- {Node: HIGH ratio}
        '''
        for key in self._stats:
            n_pass,n_high,_t = self._stats[key]
            self._stats[key]= n_pass,n_high,float(n_pass)/(n_pass+n_high)  
             
    
    def _stats_sort(self,threshold=0.5):
        '''
        In -- {Connector: PASS Number,HIGH Number,PASS ratio,...}
        Return -- [(Node,ratio),...] with decrease order ,and > threshold
        '''
        lst = sorted(self._stats.items(),key = lambda d:sum(d[1]),reverse=True)
        lst = sorted(lst,key = lambda d:d[1][2],reverse=False)
        lst = filter(lambda d:d[1][2]>threshold,lst)
        return lst
       


#def show_out(lst):
#    import matplotlib.pyplot as plt
#    import numpy as np    
#
#    Node = map(lambda b:b[0],lst)
#    Ratio = map(lambda b:b[1],lst)
#    y_pos = np.arange(len(Node))
#    
#    plt.rcdefaults()
#    plt.rcParams.update({'figure.autolayout':True})
#    fig,ax = plt.subplots(figsize=(5,len(Node)))     
#    ax.barh(y_pos,Ratio,align='center',color='red')
#    ax.set_yticks(y_pos)
#    ax.set_yticklabels(Node)
#    ax.invert_yaxis()
#    ax.set_xlabel("HIGH Ratio")
#    ax.set_title("Cable Analysis Result")
#    plt.show()
    
    
#================================================
#======================================================    
if __name__=="__main__":
    "get report_file & analysis_file "
    log_file = "./pgv/gnd.txt"
    report_file ="./pgv/gnd_sum.txt"
    prog_file ="./pgv/gnd.xlsx"  
    pgv1 = pgv(log_file,prog_file,report_file)
    pgv1.analysis()
    pgv1.report_out(0.5)
    pgv1.prog_out()

