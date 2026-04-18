# detection/rules.py
from collections import defaultdict
from datetime import datetime, timedelta

def detect_port_scan(buffer: list) -> list:
    alerts = []
    port_map = defaultdict(set)
    time_map = defaultdict(list)

    for p in buffer:
        if p["dport"]:
            port_map[p["src_ip"]].add(p["dport"])
            time_map[p["src_ip"]].append(p["timestamp"])

    for ip, ports in port_map.items():
        if len(ports) > 15:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "src_ip": ip,
                "dst_ip": "multiple",
                "rule_name": "Port Scan Detected",
                "severity": "HIGH",
                "description": f"{ip} scanned {len(ports)} ports"
            })
    return alerts

def detect_syn_flood(buffer: list) -> list:
    alerts = []
    syn_map = defaultdict(int)

    for p in buffer:
        if p.get("flags") == "S":
            syn_map[p["src_ip"]] += 1

    for ip, count in syn_map.items():
        if count > 100:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "src_ip": ip,
                "dst_ip": "multiple",
                "rule_name": "SYN Flood Detected",
                "severity": "CRITICAL",
                "description": f"{ip} sent {count} SYN packets"
            })
    return alerts

def detect_icmp_flood(buffer: list) -> list:
    alerts = []
    icmp_map = defaultdict(int)

    for p in buffer:
        if p["protocol"] == 1:  # ICMP
            icmp_map[p["src_ip"]] += 1

    for ip, count in icmp_map.items():
        if count > 50:
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "src_ip": ip,
                "dst_ip": "multiple",
                "rule_name": "ICMP Flood Detected",
                "severity": "MEDIUM",
                "description": f"{ip} sent {count} ICMP packets"
            })
    return alerts

def run_all_rules(buffer: list) -> list:
    alerts = []
    alerts.extend(detect_port_scan(buffer))
    alerts.extend(detect_syn_flood(buffer))
    alerts.extend(detect_icmp_flood(buffer))
    return alerts