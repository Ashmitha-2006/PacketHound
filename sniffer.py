# capture/sniffer.py
from scapy.all import sniff, IP, TCP, UDP, ICMP
from datetime import datetime
import threading

packet_buffer = []
buffer_lock = threading.Lock()

def process_packet(packet):
    if IP in packet:
        record = {
            "timestamp": datetime.now().isoformat(),
            "src_ip": packet[IP].src,
            "dst_ip": packet[IP].dst,
            "protocol": packet[IP].proto,
            "length": len(packet),
            "sport": packet[TCP].sport if TCP in packet else (packet[UDP].sport if UDP in packet else None),
            "dport": packet[TCP].dport if TCP in packet else (packet[UDP].dport if UDP in packet else None),
            "flags": str(packet[TCP].flags) if TCP in packet else None,
        }

        with buffer_lock:
            packet_buffer.append(record)
            if len(packet_buffer) > 1000:
                packet_buffer.pop(0)

        print(f"[+] {record['src_ip']} → {record['dst_ip']} | proto:{record['protocol']} | len:{record['length']}")
        return record

def get_buffer():
    with buffer_lock:
        return list(packet_buffer)

def clear_buffer():
    with buffer_lock:
        packet_buffer.clear()

def start_sniffing(interface=None, count=0):
    print(f"[*] PacketHound is sniffing... 🐕")
    sniff(iface=interface, prn=process_packet, store=False, count=count)

if __name__ == "__main__":
    start_sniffing()