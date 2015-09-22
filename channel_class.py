# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 11:45:48 2015

@author: ppfaff
"""

import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame
import pandas as pd
from random import random, randint


class SingleChannel():
    noise_amp = 0.05
    debug = False
    def __init__(self):
        self.dt = 1e-5
        self.interval = 500e-3
        self.mean_t_op = 20e-3
        self.mean_t_cl = 10e-3
        self.opens = []
        self.closes = []
        self.data = []
        self.cum_open = []
        self.cum_closed = []
        self.g_max = 1e-11
        self.e_zero = -95e-3
        
        
    def get_randoms(self):
        too_short = True
        samples = 10
        while too_short:
            opens = np.random.exponential(size=samples)
            closes = np.random.exponential(size=samples)
            time_covered = self.mean_t_op * sum(opens) + self.mean_t_cl * sum(closes)
            if time_covered >= self.interval:
                too_short = False
            else:
                samples *= 2
        return opens, closes
    
    @property
    def mean_ot(self):
        n_opens = len(self.cum_open)
        ot_np = np.array(self.cum_open)
        return ot_np.mean()

    @property
    def mean_ct(self):
        n_closes = len(self.cum_closed)
        ct_np = np.array(self.cum_closed)
        return ct_np.mean()

    def __call__(self, Vm=0.0, plt = "i"):
        self.cum_closed = []
        self.cum_open = []
        def trim_times(open_time, close_time, over_shoot, start_state):
            if start_state and over_shoot > close_time:
                open_time = step_time - over_shoot
                close_time = 0.0
            elif start_state and over_shoot <= close_time:
                close_time = step_time - over_shoot - open_time
            elif not start_state and over_shoot > open_time:
                close_time = step_time - over_shoot
                open_time = 0.0
            elif not start_state and over_shoot <= open_time:
                open_time = step_time - over_shoot - close_time
            return open_time, close_time
        
        def run_channel(open, closed, g_open=1, dt=self.dt, start_open=False):
            channel = []
            n_open_steps = int(open/dt)
            n_close_steps = int(closed/dt)
            opening = [g_open for i in range(n_open_steps)]
            closing = [0 for i in range(n_close_steps)]
            if start_open:
                channel = opening + closing
            else:
                channel = closing + opening
            return channel
    
        channel_data = []
        over_shot = False
        cum_time = 0.0
        p_open = self.mean_t_op/(self.mean_t_cl + self.mean_t_op)
        if random() < p_open:
            start_state = 1
        else:
            start_state = 0
        # start_state = randint(0, 1)  # initial state is 0=closed, or 1=open
        self.opens, self.closes = self.get_randoms()
        open_avg = self.opens.mean()
        closed_avg = self.closes.mean()
        if SingleChannel.debug: print(open_avg, closed_avg, start_state)
    
        for open, close in zip(self.opens, self.closes):
            open_time = open * self.mean_t_op
            close_time = close * self.mean_t_cl
            step_time = open_time + close_time
            self.cum_open.append(open_time)
            self.cum_closed.append(close_time)
            cum_time += step_time
            if cum_time > self.interval:
                over_shoot = cum_time - self.interval
                open_time, close_time = trim_times(open_time, close_time, 
                                                   over_shoot, start_state)
                over_shot = True
            channel_data += run_channel(open_time, close_time,
                                        start_open=start_state)
            if over_shot:
                break
        channel_data_np = np.array(channel_data)
        self.add_noise(channel_data, self.noise_amp)
        channel_gs = channel_data_np * self.g_max
        channel_i = channel_gs * (Vm - self.e_zero)
        channel_data_np = self.add_noise(channel_data_np, self.noise_amp)
        if plt == "g":
            channel_data_np = self.add_noise(channel_gs, self.noise_amp)
        elif plt == "i":
            channel_data_np = self.add_noise(channel_i, self.noise_amp)
        return channel_data_np

    def add_noise(self, channel_data, amp):
        noise = np.random.normal(size=len(channel_data))
        scaled_noise = noise * amp
        chan_dat_np = np.array(channel_data)+scaled_noise
        return chan_dat_np
    
if __name__ == "__main__":
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
