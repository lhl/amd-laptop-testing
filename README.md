# amd-laptop-testing
Scripts and tools for testing AMD Renoir (Ryzen 4000 series mobile) laptop

You can run `run.py` to do run a simple test:
* log to [timestamp]-data.log 
* by default, run `stress --cpu 16` for 600s and let cool for 60s
* generate graph w/ matplotlib

## Requirements
A `requirements.txt` is included for Python 3 dependencies. 

I recommend using [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Poetry](https://python-poetry.org/) for environment management.

`stress` is required for generating CPU load.

### Temperature
'Tctl' should be available via lm-sensors `sensors` either via the kernel's default k10temp or via https://github.com/ocerman/zenpower

### Power
Requires https://github.com/djselbeck/rapl-read-ryzen

Also, make sure you have the MSR kernel module enabled
```
sudo modprobe msr
```
