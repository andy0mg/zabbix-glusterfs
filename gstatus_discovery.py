#!/usr/bin/python3
import json
import subprocess
import sys

gluster_volume_names = []

def fail():
    if len(sys.argv) == 1:
        print(json.dumps({"data": []}))
    elif len(sys.argv) == 3 and sys.argv[1] == "state":
        print("down")
    else:
        print(0)
    sys.exit(1)

try:
    gstatus_output = subprocess.check_output(
        ['/usr/bin/gstatus', '-a', '-o', 'json'],
        stderr=subprocess.STDOUT,
        timeout=30
    ).decode('utf-8', errors='replace')
except Exception:
    fail()

json_start = gstatus_output.find('{')
json_end = gstatus_output.rfind('}')
if json_start == -1 or json_end == -1 or json_end < json_start:
    fail()

json_part = gstatus_output[json_start:json_end + 1]

try:
    gluster_info = json.loads(json_part)
except Exception:
    fail()

data = gluster_info.get("data", {})
volume_list = data.get("volume_summary", [])

nargs = len(sys.argv)

if nargs == 1:
    for volume in volume_list:
        if volume.get("name"):
            gluster_volume_names.append({"{#VOLUME_NAME}": volume["name"]})
    print(json.dumps({"data": gluster_volume_names}))

elif nargs == 2:
    key = sys.argv[1]

    if key == "heal_entries":
        total = 0
        for volume in volume_list:
            for item in volume.get("healinfo", []):
                try:
                    total += int(item.get("nr_entries", 0))
                except (TypeError, ValueError):
                    pass
        print(total)

    elif key == "heal_active":
        total = 0
        for volume in volume_list:
            for item in volume.get("healinfo", []):
                try:
                    total += int(item.get("nr_entries", 0))
                except (TypeError, ValueError):
                    pass
        print(1 if total > 0 else 0)

    else:
        value = data.get(key, 0)
        if value in (None, ''):
            print(0)
        else:
            print(value)

elif nargs == 3:
    for volume in volume_list:
        if volume.get("name") and sys.argv[2] == volume["name"]:
            value = volume.get(sys.argv[1], 0)
            if value in (None, ''):
                if sys.argv[1] == "state":
                    print("down")
                else:
                    print(0)
            else:
                print(value)
            break
    else:
        if sys.argv[1] == "state":
            print("down")
        else:
            print(0)

else:
    print("Wrong arguments")
