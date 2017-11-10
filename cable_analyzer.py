#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 13:12:27 2017

@author: appel
"""
import sys
import re

def list_of_report(filename):
    '''
    In -- TXT file of testing report
    Return -- [[ ],...]
    '''
    lines = []
    fp = open(filename,U'r')
    i = 0
    for line in fp:
        info = line_process(line)
        if info and info[0]==':':
            if i%2==0:
                lines.append(info[1:])
            else:
                lines[i/2].extend(info[1:])
            i += 1;
    return lines
        
def line_process(rawline):
    '''
    In -- text line
    Return -- [ , , ,]    
    '''
    info = rawline.split()
    return info
    
def nodename(pin_name):
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

def node_and_value(lines):
    '''
    In -- [code,addr_a,pin_a,addr_b,status,value,unit,pin_b],
        a line of testing result
    Return -- [status, pin_a, pin_b, value]
    '''
    result = []
    for line in lines:
            pin_a = line[2]
            pin_b = line[7]
            result.append([line[4],nodename(pin_a),nodename(pin_b),line[5]])
    return result
 
def counting(infos):
    '''
    {'NodeName':(PASS number,HIGH number)}
    '''
    result = dict()
    for info in infos:
        status,nodeA,nodeB,value = info
        valueA = result.get(nodeA,(0,0))
        valueB = result.get(nodeB,(0,0))
        if status == 'PASS':
            result[nodeA] = (valueA[0]+1,valueA[1])
            result[nodeB] = (valueB[0]+1,valueB[1])
        elif status =='HIGH':
            result[nodeA] = (valueA[0],valueA[1]+1)
            result[nodeB] = (valueB[0],valueB[1]+1)
    return result
    
def statistic(result):
    '''
    calculate the ratio of HIGH result
    In -- {Node:(PASS number,HIGH number)}
    Return -- {Node: HIGH ratio}
    '''
    dic = dict()
    for res in result:
        n_pass,n_high = result[res]
        dic[res]= float(n_high)/(n_pass+n_high)  
    
    return dic         

def s_f(dic,threshold=0.5):
    '''
    In -- {Node: HIGH ratio,...}
    Return -- [(Node,ratio),...] with decrease order ,and > threshold
    '''
    dic = sorted(dic.items(),key = lambda d:d[1],reverse=True) 
    lst = filter(lambda d:d[1]>0.5,dic)
    return lst
   
def string_out(lst,out=None):
    '''
    print out
    '''
    str_line = "===Node Name===HIGH Ratio===\n" 
    for item in lst:
        str_line += "%12s%10.2f%%\n"%(item[0],item[1]*100)
        
    if out:
        fp = open(out,'w') 
        fp.write(str_line)
        
    return str_line

def show_out(lst):
    import matplotlib.pyplot as plt
    import numpy as np    

    Node = map(lambda b:b[0],lst)
    Ratio = map(lambda b:b[1],lst)
    y_pos = np.arange(len(Node))
    
    plt.rcdefaults()
    plt.rcParams.update({'figure.autolayout':True})
    fig,ax = plt.subplots(figsize=(5,len(Node)))     
    ax.barh(y_pos,Ratio,align='center',color='red')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(Node)
    ax.invert_yaxis()
    ax.set_xlabel("HIGH Ratio")
    ax.set_title("Cable Analysis Result")
    plt.show()
    
if __name__=="__main__":
    "get report_file & analysis_file "
    report_file = "point.txt"
    if len(sys.argv)==2:
        report_file,analysis_file = sys.argv[1],None
    elif len(sys.argv)>2:
        report_file,analysis_file = sys.argv[1],sys.argv[2]
    index = report_file.rfind(".")
    if index ==-1:
        analysis_file = report_file+"_sum"
    else:
        analysis_file = report_file[:index]+"_sum"+report_file[index:]
        
    " "           
    lists = list_of_report(report_file)
    #print(lists)
    infos = node_and_value(lists)
    result = counting(infos)
    res=statistic(result)
    res=s_f(res)
    show_out(res)
    string=string_out(res,analysis_file)
    print(string)