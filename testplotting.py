# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 07:53:30 2015

@author: ppfaff
"""

import pyqtgraph as pg
import matplotlib.pyplot as plt
from channel_class import SingleChannel
from pandas import DataFrame
import cProfile
import pstats


def use_pyqtgraph():
    sc = SingleChannel()
    channel_data = sc()
    channel_times = [i*sc.dt for i in range(len(channel_data))]
    
    pg.plot(channel_times, channel_data)

def use_matpltlab():
    sc = SingleChannel()
    channel_data = sc()
    channel_times = [i*sc.dt for i in range(len(channel_data))]
    #noise_amp = 0.05
    #chan_dat_np = sc.add_noise(channel_data, noise_amp)
        
    
    data = {'time': channel_times, 'record': channel_data}

    my_record = DataFrame(data)
    # my_record.plot() 
    plt.plot(data['time'], data['record'])
    # plt.axes([0.0, 0.3, 0, 1.5])
    plt.show()


prof1 = cProfile.Profile()
prof2 = cProfile.Profile()

prof1.runcall(use_pyqtgraph)
prof2.runcall(use_matpltlab)

print("Stats for pyqtgraph")
stat1 = pstats.Stats(prof1)
stat1.strip_dirs()
stat1.sort_stats('cumulative')
stat1.print_stats(20)

print("Stats for matpltlab")

stat2 = pstats.Stats(prof2)
stat2.strip_dirs()
stat2.sort_stats('cumulative')
stat2.print_stats(20)
