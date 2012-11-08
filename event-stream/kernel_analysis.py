
from __future__ import print_function

import argparse
import os
import itertools as it
import sys

import numpy as np
import matplotlib.pyplot as plt

from events import *

class AwakeDurations(object):
    subpath = "awake-durations"

    def __init__(self):
        self.durations = []
        self.awaken_time = None
        self.started = False

    def process_event(self, event):
        if not self.started:
            self.started = True
            self.awaken_time = event.timestamp

        elif event.event == 'RESUME':
            assert self.awaken_time == None
            self.awaken_time = event.timestamp

        elif event.event == 'SUSPEND':
            assert self.awaken_time != None
            duration = event.timestamp - self.awaken_time
            self.durations.append(duration)
            self.awaken_time = None

    def persist(self, path):
        dname = os.path.join(path, self.subpath)
        if not os.path.exists(dname):
            os.makedirs(dname)
        fname = os.path.join(dname, 'durations')
        with open(fname, 'w') as f:
            for d in self.durations:
                f.write('%d\n'%d)

    def merge(self, paths):
        for path in paths:
            fname = os.path.join(path, self.subpath, 'durations')
            with open(fname, 'r') as f:
                for line in f:
                    self.durations.append(int(line))

    def plot(self):
        if len(self.durations) > 0:
            plt.hist(self.durations, bins=200)
            plt.title("Distribution of Awake Durations")
            plt.xlabel("Awake Duration")
            plt.ylabel("Count")
            plt.show()

class SleepDurations(object):
    subpath = "sleep-durations"

    def __init__(self):
        self.durations = []
        self.sleep_time = None
    
    def process_event(self, event):
        if event.event == 'SUSPEND':
            assert self.sleep_time == None
            self.sleep_time = event.timestamp

        elif event.event == 'RESUME':
            assert self.sleep_time != None
            duration = event.timestamp - self.sleep_time
            self.durations.append(duration)
            self.sleep_time = None

    def persist(self, path):
        dname = os.path.join(path, self.subpath)
        if not os.path.exists(dname):
            os.makedirs(dname)
        fname = os.path.join(dname, 'durations')
        with open(fname, 'w') as f:
            for d in self.durations:
                f.write('%d\n'%d)

    def merge(self, paths):
        for path in paths:
            fname = os.path.join(path, self.subpath, 'durations')
            with open(fname, 'r') as f:
                for line in f:
                    self.durations.append(int(line))

    def plot(self):
        if len(self.durations) > 0:
            plt.hist(self.durations, bins=200)
            plt.title("Distribution of Sleep Durations")
            plt.xlabel("Sleep Duration")
            plt.ylabel("Count")
            plt.show()
            

class AwakeTimePerDay(object):
    def __init__(self):
        self.data = []

def analyze(istream, path, statistics):
    estream = it.imap(decode_event_tuple, istream)

    for event in estream:
        for stat in statistics:
            stat.process_event(event)

    for stat in statistics:
         stat.persist(path)

def plot(paths, statistics):
    for stat in statistics:
        stat.merge(paths)
        stat.plot()

def main():
    statistics = []
    statistics.append(AwakeDurations())
    statistics.append(SleepDurations())

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--analyze', dest='analyze', action='store_true')
    parser.add_argument('-o', '--outpath', dest='outpath')
    parser.add_argument('-p', '--plot', dest='plot', action='store_true')
    parser.add_argument('paths', nargs='*')

    args = parser.parse_args()
    if args.analyze:
        if args.outpath == None:
            exit("Error: must specify output path")
        analyze(sys.stdin, args.outpath, statistics)
    
    if args.plot:
        if len(args.paths) == 0:
            exit("Error: must specify one or more input paths")
        plot(args.paths, statistics)

if __name__ == "__main__":
    main()




