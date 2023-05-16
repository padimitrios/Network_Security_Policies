# Device authentication
RSA digital signature scheme

## Topology
<p align="center">
  <img src="device_authentication.png" alt="Network topology." width="700" height="700">
</p>

## `Output`
<code>  
0: 192.168.0.2 received packet: U dun say so early hor... U c already then say... <br>
0: Packet forwarded.<br>
1: 192.168.0.2 received packet: Nah I dont think he goes to usf, he lives around here though<br>
1: Packet forwarded.<br>
2: 192.168.0.2 received packet: Nah I dont think he goes to usf, he lives around here though<br>
2: Packet forwarded.<br>
3: Invalid signature from 192.168.0.3, packet dropped.<br>
4: 192.168.0.2 received packet: Ok lar... Joking wif u oni...<br>
4: Packet forwarded.<br>
5: Malicious packet from 192.168.0.3 dropped.<br>
5: Sender 192.168.0.3 appended on blacklist<br>
6: Untrusted sender 192.168.0.3 tried to communicate with 192.168.0.2. Packet dropped.<br>
7: Malicious packet from 192.168.0.1 dropped.<br>
7: Sender 192.168.0.1 appended on blacklist<br>
8: Untrusted sender 192.168.0.3 tried to communicate with 192.168.0.2. Packet dropped.<br>
9: Untrusted sender 192.168.0.3 tried to communicate with 192.168.0.2. Packet dropped.
10: 192.168.0.2 received packet: U dun say so early hor... U c already then say...<br>
10: Packet forwarded.<br>
11: Untrusted sender 192.168.0.1 tried to communicate with 192.168.0.2. Packet dropped.<br>
12: Untrusted sender 192.168.0.1 tried to communicate with 192.168.0.2. Packet dropped.<br>
13: Untrusted sender 192.168.0.1 tried to communicate with 192.168.0.2. Packet dropped.<br>
14: 192.168.0.2 received packet: Nah I dont think he goes to usf, he lives around here though<br>
14: Packet forwarded.<br>
15: Untrusted sender 192.168.0.1 tried to communicate with 192.168.0.2. Packet dropped.<br>
16: Untrusted sender 192.168.0.1 tried to communicate with 192.168.0.2. Packet dropped.<br>
<strong>17: Invalid signature from 192.168.0.4, packet dropped.</strong><br>
18: 192.168.0.2 received packet: U dun say so early hor... U c already then say...<br>
18: Packet forwarded.<br>
19: 192.168.0.2 received packet: U dun say so early hor... U c already then say...<br>
19: Packet forwarded.<br>
</code>

### In packet message 17 the message was tempered
