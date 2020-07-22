#!/usr/bin/env python


import delegator
import matplotlib.pyplot as plt
import multiprocessing as mp
import pandas as pd
import statistics
import time


START = time.time()
PRE_RUN = 20
RUN = 300
POST_RUN = 60


def logger(keep_logging):
  log_name = '{}-data.log'.format(int(START))
  print('Logging to {}'.format(log_name))
  log = open(log_name, 'w') 

  while keep_logging.value:
    tick = time.time()

    # Temperature 
    c = delegator.run('sensors | grep Tctl')
    temp = c.out.split()[1][1:][:-2]

    # Package Power
    c = delegator.run('./ryzen | grep Package')
    power = c.out.split('\n')
    power.pop()
    power = [float(x.split()[-1][:-1]) for x in power]
    power = round(statistics.mean(power), 2)

    # Clock Speed
    c = delegator.run('cat /proc/cpuinfo | grep MHz')
    clock = c.out.split('\n')
    clock.pop()
    clock = [float(x.split()[-1]) for x in clock]
    clock = round(statistics.mean(clock))

    print('  {},{},{},{}'.format(int(tick),temp, power, clock))
    log.write('{},{},{},{}\n'.format(int(tick),temp, power, clock))

    # Next second
    tock = time.time()
    diff = tock - tick
    time.sleep(1-diff)

  # When cancelling
  log.close()


def stress():
  print('Running stress test for {} seconds'.format(RUN))
  c = delegator.run('stress -c 16 -t {}'.format(RUN))


def makeplot():
  # https://matplotlib.org/3.1.1/gallery/ticks_and_spines/multiple_yaxis_with_spines.html#sphx-glr-gallery-ticks-and-spines-multiple-yaxis-with-spines-py
  def make_patch_spines_invisible(ax):
    ax.set_frame_on(True)
    ax.patch.set_visible(False)
    for sp in ax.spines.values():
      sp.set_visible(False)

  # Data Loading
  df = pd.read_csv('{}-data.log'.format(int(START)),
                   names=['time','temp','power','clock']
                  )
  # start from 0 time
  start = df['time'][0]
  df['time'] = df['time'].apply(lambda x: x - start)

  # Graph
  fig, host = plt.subplots()
  fig.subplots_adjust(right=0.75)

  par1 = host.twinx()
  par2 = host.twinx()

  # Offset the right spine of par2.  The ticks and label have already been
  # placed on the right by twinx above.
  par2.spines["right"].set_position(("axes", 1.2))
  # Having been created by twinx, par2 has its frame off, so the line of its
  # detached spine is invisible.  First, activate the frame but make the patch
  # and spines invisible.
  make_patch_spines_invisible(par2)
  # Second, show the right spine.
  par2.spines["right"].set_visible(True)

  p1, = host.plot(df['time'].tolist(), df['temp'].tolist(), "r-", label="temp")
  p2, = par1.plot(df['time'].tolist(), df['power'].tolist(), "b-", label="power")
  p3, = par2.plot(df['time'].tolist(), df['clock'].tolist(), "g-", label="clock")

  host.set_xlim(0, df['time'].max())
  host.set_ylim(30, 90) # Temp
  par1.set_ylim(0, 70) # Power
  par2.set_ylim(1000, 4500) # Clock

  host.set_xlabel("Time (s)")
  host.set_ylabel("Temperature (C)")
  par1.set_ylabel("Power (W)")
  par2.set_ylabel("Clock (MHz)")

  host.yaxis.label.set_color(p1.get_color())
  par1.yaxis.label.set_color(p2.get_color())
  par2.yaxis.label.set_color(p3.get_color())

  tkw = dict(size=4, width=1.2)
  host.tick_params(axis='y', colors=p1.get_color(), **tkw)
  par1.tick_params(axis='y', colors=p2.get_color(), **tkw)
  par2.tick_params(axis='y', colors=p3.get_color(), **tkw)
  host.tick_params(axis='x', **tkw)

  lines = [p1, p2, p3]

  # host.legend(lines, [l.get_label() for l in lines])

  figure = plt.gcf()
  figure.set_size_inches(12, 4)
  plt.savefig('{}-graph.png'.format(int(START)), dpi=100)
  # plt.show()


if __name__ == '__main__':
  keep_logging = mp.Value('i', 1)

  # Start logging
  l = mp.Process(target=logger, args=(keep_logging,))
  l.start()

  # Baseline
  time.sleep(PRE_RUN)

  # Start stress-test
  s = mp.Process(target=stress)
  s.start()

  # Wait until it's over...
  s.join()

  # Cooldown
  print('Cooling down for {} seconds'.format(POST_RUN))
  time.sleep(POST_RUN)

  # Stop the Logger
  keep_logging.value = 0
  l.join()

  # Make plot
  makeplot()

###
# Notes/title
'''
* Plugged
  * Normal
  * Speed
* Unplugge
'''
# Log Time (thread)
# New File
# After 10s run stress --cpu 16
# for 600s
# Let cool for 60s 
# Stop Logging
# Generatete

'''
https://github.com/FlyGoat/RyzenAdj
sudo ryzenadj -f 95
sudo ryzenadj --stapm-limit=45000 --fast-limit=45000 --slow-limit=45000 --tctl-temp=90
'''
