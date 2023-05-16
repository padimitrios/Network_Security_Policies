# Device authentication
RSA digital signature scheme

## Topology
<p align="center">
  <img src="device_authentication.png" alt="Network topology." width="700" height="700">
</p>

## `Output`
<code>0: 192.168.0.2 received packet: U dun say so early hor... U c already then say... <br></code>
<code>0: Packet forwarded.<br></code>
<code>1: 192.168.0.2 received packet: Nah I dont think he goes to usf, he lives around here though<br></code>
<code>1: Packet forwarded.<br></code>
<code>2: 192.168.0.2 received packet: Nah I dont think he goes to usf, he lives around here though<br></code>
<code>2: Packet forwarded.<br></code>
<code>3: Invalid signature from 192.168.0.3, packet dropped.<br></code>
<code>4: 192.168.0.2 received packet: Ok lar... Joking wif u oni...<br></code>
<code>4: Packet forwarded.<br></code>
<code>5: Malicious packet from 192.168.0.3 dropped.<br></code>
<code>5: Sender 192.168.0.3 appended on blacklist<br></code>
<code>6: Untrusted sender 192.168.0.3 tried to communicate with 192.168.0.2. Packet dropped.<br></code>
<code>7: Malicious packet from 192.168.0.1 dropped.<br></code>
<code>7: Sender 192.168.0.1 appended on blacklist<br></code>
<code>8: Untrusted sender 192.168.0.3 tried to communicate with 192.168.0.2. Packet dropped.<br></code>
<code>9: Untrusted sender 192.168.0.3 tried to communicate with 192.168.0.2. Packet dropped.<br></code>
<code>10: 192.168.0.2 received packet: U dun say so early hor... U c already then say...<br></code>
<code>10: Packet forwarded.<br></code>
<code>11: Untrusted sender 192.168.0.1 tried to communicate with 192.168.0.2. Packet dropped.<br></code>
<code>12: Untrusted sender 192.168.0.1 tried to communicate with 192.168.0.2. Packet dropped.<br></code>
<code>13: Untrusted sender 192.168.0.1 tried to communicate with 192.168.0.2. Packet dropped.<br></code>
<code>14: 192.168.0.2 received packet: Nah I dont think he goes to usf, he lives around here though<br></code>
<code>14: Packet forwarded.<br></code>
<code>15: Untrusted sender 192.168.0.1 tried to communicate with 192.168.0.2. Packet dropped.<br></code>
<code>16: Untrusted sender 192.168.0.1 tried to communicate with 192.168.0.2. Packet dropped.<br></code>
<code><strong>17: Invalid signature from 192.168.0.4, packet dropped.</strong><br></code>
<code>18: 192.168.0.2 received packet: U dun say so early hor... U c already then say...<br></code>
<code>18: Packet forwarded.<br></code>
<code>19: 192.168.0.2 received packet: U dun say so early hor... U c already then say...<br></code>
<code>19: Packet forwarded.<br></code>

### In packet 17 the message was tempered
