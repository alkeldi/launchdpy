# launchdpy
OSX's  launchd communicator. (Communicate with launchd from python).

# Dependencies
+ Place [launch.py](https://github.com/alkeldi/launch.py) in the same directory as launchdpy.py


## Example 1: List a single job's info

```python
import launchpy

job = launchpy.launchMsg({"GetJob": "com.apple.geod"}) #assuming com.apple.geod is out target job
print(job)
```


## Example 2: Imitate  *launchctl*

```python
import launchpy

jobs = launchpy.launchMsg("GetJobs")
for label in jobs:
    PID = "?"
    LastExitStatus = "?"
    if "PID" in jobs[label]:
        PID = jobs[label]["PID"]
    if "LastExitStatus" in jobs[label]:
        LastExitStatus = jobs[label]["LastExitStatus"]
    print(PID, "\t", LastExitStatus, "\t", label)
```


# Important Notes
+ "GetJob" and "GetJobs" are two of many values that can be used to comunicate with launchd. A full list of these values is found in [launch.py](https://github.com/alkeldi/launch.py)

