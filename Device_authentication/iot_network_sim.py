import simpy
import string
import random
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
import cryptography.exceptions
from datetime import datetime
import json

class SDNController:

  def __init__(self, env):
    self.env = env
    self.routing_table = {}
    self.public_keys_table = {}

  def add_flow(self, sender, sender_public_key, receiver):
    self.routing_table[sender] = receiver
    self.public_keys_table[sender] = sender_public_key

  def verify_signature(self, sender, packet):
    message_bytes = packet['message_bytes']
    signature = packet['signature']
    public_key = self.public_keys_table[sender]

    return public_key.verify(signature, message_bytes,
                             ec.ECDSA(hashes.SHA256()))

  def packet_from_switch(self, switch, sender, receiver, packet):

    if self.routing_table[sender] != receiver.ip:
      print(
        f"{self.env.now}: Anothorized communication from {sender}, packet dropped."
      )

    try:
      self.verify_signature(sender, packet)
      print(
        f"{self.env.now}: Sender:{sender}, verified using digital signature.")
      switch.forward_packet(packet, receiver)
    except cryptography.exceptions.InvalidSignature:
      switch.blacklist.append(sender)
      print(
        f"{self.env.now}: Invalid signature from {sender}, packet dropped.")
      print(f"{self.env.now}: Sender {sender} appended on blacklist")
      return

class Host:

  def __init__(self, env, id, ip, ):
    self.env = env
    self.ip = ip
    self.id = id
    key_pair = generate_key_pair()
    self.private_key = key_pair[0]
    self.public_key = key_pair[1]

  def send_packet(self, packet, receiver, switch):
    switch.receive_packet(self.ip, receiver, packet)

  def receive_packet(self, packet):
    print(f"{self.env.now}: {self.ip} received packet: {packet['message_bytes'].decode('utf-8')}")

  def get_sensors_value(self, min_value, max_value):
    return round(random.uniform(min_value, max_value),2)

  def sign_message(self, message):
    return self.private_key.sign(message, ec.ECDSA(hashes.SHA256()))

  def generate_packet(self):
    
    message = {
      "device_id": str(self.id),
      "timestamp": datetime.now().isoformat(),
      "ip": str(self.ip),
      "value": str(self.get_sensors_value(0,60))
    }

    # Encoding the message into bytes
    encoded_message = json.dumps(message).encode('utf-8')

    signature = self.sign_message(encoded_message)
    packet = {'signature': signature, 'message_bytes': encoded_message}
    
    return packet


class Switch:

  def __init__(self, env, controller):
    self.env = env
    self.controller = controller
    self.blacklist = []

  def receive_packet(self, sender, receiver, packet):
    if sender in self.blacklist:
      print(
        f"{self.env.now}: Untrusted sender {sender} tried to communicate with {receiver.ip}. Packet dropped."
      )
    else:

      #10% chance to temper a message
      random_number = random.randint(1, 10)
      if random_number == 2:
        byte_to_append = b'\x58'
        packet['message_bytes'] = packet['message_bytes'] + byte_to_append

      self.controller.packet_from_switch(self, sender, receiver, packet)

  def forward_packet(self, packet, receiver):
    print(f"{self.env.now}: Packet forwarded.")
    self.send_packet(packet, receiver)

  def send_packet(self, packet, receiver):
    receiver.receive_packet(packet)


def generate_key_pair():
  private_key = ec.generate_private_key(ec.SECP384R1())
  return [private_key, private_key.public_key()]

# Generate a random ID
def generate_random_id(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

if __name__ == '__main__':
  env = simpy.Environment()
  host1 = Host(env, generate_random_id(), "192.168.0.1")
  host3 = Host(env, generate_random_id(), "192.168.0.3")
  host4 = Host(env, generate_random_id(), "192.168.0.4")
  host2 = Host(env, generate_random_id(), "192.168.0.2")

  controller = SDNController(env)
  switch = Switch(env, controller)

  controller.add_flow(host1.ip, host1.public_key, host2.ip)
  controller.add_flow(host3.ip, host3.public_key, host2.ip)
  controller.add_flow(host4.ip, host4.public_key, host2.ip)

  # create a simulation process for host1 to send packets to host2 via switch
  def send_packets(env, terminals, receiver, switch, num_packets):
    for i in range(num_packets):
      sender = random.choice(terminals)
      packet = sender.generate_packet()
      sender.send_packet(packet, receiver, switch)
      yield env.timeout(1)

  terminals = [host1, host3, host4]
  # start the simulation process
  env.process(send_packets(env, terminals, host2, switch, 20))
  env.run()
