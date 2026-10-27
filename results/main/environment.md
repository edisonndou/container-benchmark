# Measurement environment
Recorded (UTC): 2026-10-27T09:10:20Z
Recorded by: lenovo_edison

## Host
```
Linux eCodeTech 6.18.54.1-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Tue Oct  6 19:13:07 UTC 2026 x86_64 GNU/Linux

Ubuntu 26.04.1 LTS

Architecture:                            x86_64
CPU(s):                                  12
Model name:                              AMD Ryzen 5 5600H with Radeon Graphics
Thread(s) per core:                      2
Core(s) per socket:                      6
Socket(s):                               1

               total        used        free      shared  buff/cache   available
Mem:           6.7Gi       909Mi       2.6Gi       4.3Mi       3.4Gi       5.8Gi
Swap:          2.0Gi          0B       2.0Gi

CPU governor: n/a (VM or no cpufreq)
Virtualization: wsl
On AC power: 1
Load average at record time: 1.34 0.48 0.19
```

## Tools
```
docker:    29.9.2
storage:   overlayfs / cgroup 2 / Ubuntu 26.04.1 LTS
node:      v22.22.1
autocannon: autocannon v8.0.0
syft:      Version:       1.55.0
trivy:     Version: 0.76.1
python:    Python 3.14.4
```

## Fixed experiment settings (scripts/common.sh)
```
CPUS=1
MEMORY=256m
NODE_VERSION=22.22.0
HOST_PORT=8080
```
