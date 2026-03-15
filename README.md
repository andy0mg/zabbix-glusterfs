# Zabbix GlusterFS Monitoring Template

## Overview

This project provides a **Zabbix template and helper script to monitor a GlusterFS cluster** using the `gstatus` utility.

The solution collects cluster and volume metrics from GlusterFS and exposes them to Zabbix using a Python script and `UserParameter` items.

The template supports:

- Gluster cluster health monitoring
- Node availability monitoring
- Volume discovery (LLD)
- Brick availability monitoring
- Volume usage monitoring
- Self-heal queue monitoring

The monitoring relies on the JSON output of:

```
gstatus -a -o json
```

The script parses this JSON and returns values requested by Zabbix.

---

# Architecture

Monitoring workflow:

```
Zabbix
   ↓
Zabbix Agent
   ↓
gstatus_discovery.py
   ↓
gstatus -a -o json
   ↓
GlusterFS Cluster
```

The script extracts:

- cluster health
- number of nodes
- active nodes
- volume list
- brick status
- storage usage
- self-heal queue

---

# Features

## Cluster Metrics

| Metric | Description |
|------|-------------|
cluster_status | Overall Gluster cluster health |
nodes_active | Number of active nodes |
node_count | Total cluster nodes |
volume_count | Number of volumes |
online | Number of online bricks |
heal_entries | Pending self-heal entries |

---

## Volume Metrics (LLD)

Volumes are automatically discovered using Zabbix Low-Level Discovery.

Metrics collected per volume:

| Metric | Description |
|------|-------------|
size_total | Total volume size |
size_used | Used volume size |
free_space | Free space percentage |
status | Volume state |
health | Volume health |
online | Number of online bricks |
num_bricks | Total bricks in volume |

---

# Triggers

## Cluster Health

### Cluster unhealthy

```
Gluster volume status is Unhealthy
```

Expression:

```
find(gluster_storage_info["cluster_status"],,"like","Healthy")=0
```

---

### Cluster nodes offline

```
Gluster storage nodes is not online
```

Expression:

```
last(gluster_storage_info["nodes_active"]) < last(gluster_storage_info["node_count"])
```

---

## Self-Heal Monitoring

Two alert levels are implemented.

### Warning

```
GlusterFS: Self-heal pending entries
```

Expression:

```
min(gluster_storage_info[heal_entries],20m) > 5
```

### High Severity

```
GlusterFS: Self-heal pending entries
```

Expression:

```
min(gluster_storage_info[heal_entries],1h) > 50
```

This detects long-running or stuck self-heal operations.

---

## Volume Monitoring

### Volume health

```
Gluster Volume state in {#VOLUME_NAME} is down
```

---

### Volume free space

```
Gluster Volume Free Space is less than 20%
```

---

### Brick failure

```
GlusterFS: Volume {#VOLUME_NAME} has offline bricks
```

Expression:

```
online < num_bricks
```

This detects missing or offline bricks.

---

# Installation

## 1 Install gstatus

The script requires the `gstatus` utility.

Repository:

https://github.com/gluster/gstatus

Example installation:

```bash
pip3 install gstatus
```

---

## 2 Install the script

Copy the script to the Zabbix scripts directory.

Example:

```
/etc/zabbix/scripts/gstatus_discovery.py
```

Make it executable:

```bash
chmod +x /etc/zabbix/scripts/gstatus_discovery.py
```

---

## 3 Configure sudo access

Allow the Zabbix user to execute the script.

Example `/etc/sudoers` entry:

```
zabbix ALL=(ALL) NOPASSWD: /etc/zabbix/scripts/gstatus_discovery.py
```

---

## 4 Configure Zabbix agent

Create a configuration file:

```
/etc/zabbix/zabbix_agentd.d/gluster.conf
```

Add:

```
UserParameter=gluster_storage_info[*],sudo /etc/zabbix/scripts/gstatus_discovery.py $1
UserParameter=gluster_volume_info[*],sudo /etc/zabbix/scripts/gstatus_discovery.py $1 $2
UserParameter=gluster_volume_name.discovery,sudo /etc/zabbix/scripts/gstatus_discovery.py
```

Restart the agent:

```bash
systemctl restart zabbix-agent
```

---

## 5 Import template

Import the template XML:

```
zabbix_template.xml
```

In Zabbix:

```
Configuration → Templates → Import
```

Attach the template to the host where the script runs.

---

# Recommended Deployment

Attach the template to **one Gluster node only**.

Because `gstatus` returns cluster-wide information.

Monitoring from multiple nodes will create duplicate alerts.

---

# Requirements

- Zabbix 6.4+
- GlusterFS 9.2+
- Python 3
- gstatus utility

---

# License

This project is based on the original work:

Original author  
MrCirca

Repository:  
https://github.com/MrCirca/zabbix-glusterfs

Additional modifications and extended functionality included.
