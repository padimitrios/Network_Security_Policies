import simpy
import random
import joblib
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
import pickle
from Crypto.PublicKey import RSA
from hashlib import sha512

messages_array_bytes = [
  b'Go until jurong point, crazy.. Available only in bugis n great world la e buffet... Cine there got a...',
  b'Ok lar... Joking wif u oni...',
  b'Free entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005. Text FA to 87121 to receive entry question(std txt rate)T&Cs apply 08452810075over18s',
  b'U dun say so early hor... U c already then say...',
  b'Nah I dont think he goes to usf, he lives around here though',
  b'FreeMsg Hey there darling its been 3 weeks now and no word back! Id like some fun you up for it still? Tb ok! XxX std chgs to send, 1.50 to rcv',
]

class SDNController:

    def __init__(self, env, model):
        self.env = env
        self.classifier = Classifier(model)
        self.routing_table = {}
        self.public_keys_table = {}
        self.n_keys_table = {}

    def add_flow(self, sender, sender_public_key, n,receiver):
        # add the connection and the public keys of the sender to the controller
        self.routing_table[sender] = receiver
        self.public_keys_table[sender] = sender_public_key
        self.n_keys_table[sender] = n

    def verify_signature(self, sender, packet):
        # create the new hash from the message sent and verify
        hash = int.from_bytes(sha512(packet['message_bytes']).digest(), byteorder='big')
        hashFromSignature = pow(packet['signature'], int(self.public_keys_table[sender]), int(self.n_keys_table[sender]))

        return hash == hashFromSignature

    def packet_from_switch(self, switch, sender, receiver, packet):

        if self.routing_table[sender] != receiver.ip:
            print(f"{self.env.now}: Anothorized communication from {sender}, packet dropped.")
            return

        if not self.verify_signature(sender, packet):
            print(f"{self.env.now}: Invalid signature from {sender}, packet dropped.")
            return

        if self.classifier.classify(packet):
            print(f"{self.env.now}: Malicious packet from {sender} dropped.")
            return

        if not ((sender in switch.blacklist)):
            switch.blacklist.append(sender)
            print(f"{self.env.now}: Sender {sender} appended on blacklist")
        else:
            switch.forward_packet(packet, receiver)


class Host:
    def __init__(self, env, ip):
        self.env = env
        self.ip = ip
        key_pair = generate_key_pair()
        self.private_key = key_pair[0]  #d
        self.public_key = key_pair[1]  #e
        self.n = key_pair[2]

    def send_packet(self, packet, receiver, switch):
        switch.receive_packet(self.ip, receiver, packet)

    def receive_packet(self, packet):
        print(f"{self.env.now}: {self.ip} received packet: {packet['message_bytes'].decode('utf-8')}")

    #sign the message with private key
    def sign_message(self, hash):
        return pow(hash, int(self.private_key), int(self.n))

    def generate_packet(self):
        random_message_bytes = random.choice(messages_array_bytes)
        hash = int.from_bytes(sha512(random_message_bytes).digest(), byteorder='big')
        signature = self.sign_message(hash)

        packet = {'hash': hash, 'signature': signature, 'message_bytes':random_message_bytes}
        return packet


class Switch:

    def __init__(self, env, controller):
        self.env = env
        self.controller = controller
        self.blacklist = []

    def receive_packet(self, sender, receiver, packet):

        if sender in self.blacklist:
            print(f"{self.env.now}: Untrusted sender {sender} tried to communicate with {receiver.ip}. Packet dropped.")
        else:
            #10% change to temper a message
            random_number = random.randint(1, 10)
            if random_number == 5:
                byte_to_append = b'\x58'
                packet['message_bytes']  = packet['message_bytes']  + byte_to_append
            
        self.controller.packet_from_switch(self, sender, receiver, packet)

    def forward_packet(self, packet, receiver):
        self.send_packet(packet, receiver)
        print(f"{self.env.now}: Packet forwarded.")

    def send_packet(self, packet, receiver):
        receiver.receive_packet(packet)


class Classifier:

    def __init__(self, model):
        self.model = model

    def classify(self, packet):
        new_message = packet['message_bytes'].decode('utf-8')
        new_message = re.sub('[^a-zA-Z]', ' ', new_message)
        new_message = new_message.lower()
        new_message = new_message.split()
        new_message = [
            ps.stem(word) for word in new_message
            if not word in stopwords.words('english')
        ]
        new_message = ' '.join(new_message)

        # convert the preprocessed message into a feature vector
        new_message = cv.transform([new_message]).toarray()

        # make the prediction
        result = self.model.predict(new_message)[0]

        return result

def generate_key_pair():
    # generate public and private keys
    keyPair = RSA.generate(bits=1024)
    e = keyPair.e
    d = keyPair.d
    n = keyPair.n

    return [d, e, n]


if __name__ == '__main__':
    env = simpy.Environment()
    host1 = Host(env, "192.168.0.1")
    host3 = Host(env, "192.168.0.3")
    host4 = Host(env, "192.168.0.4")
    host2 = Host(env, "192.168.0.2")

    model = joblib.load('Prediction model/model.pkl')
    
    # initialize controller and switch
    controller = SDNController(env, model)
    switch = Switch(env, controller)

    # add the hosts and their public keys to the controller
    controller.add_flow(host1.ip, host1.public_key, host1.n, host2.ip)
    controller.add_flow(host3.ip, host3.public_key, host3.n, host2.ip)
    controller.add_flow(host4.ip, host4.public_key, host4.n, host2.ip)

    # for message classification
    cv = CountVectorizer(max_features=4000)
    ps = PorterStemmer()
    # Load the corpus list
    with open('corpus.pkl', 'rb') as f:
        corpus = pickle.load(f)

    # fit the CountVectorizer again with the updated corpus
    cv.fit(corpus)

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
