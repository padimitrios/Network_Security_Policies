import simpy
import random
import joblib
import string
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
import pickle

#malicious and normal messages for network simulation
messages_array = [
    'Go until jurong point, crazy.. Available only in bugis n great world la e buffet... Cine there got a...',
    'Ok lar... Joking wif u oni...',
    'Free entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005. Text FA to 87121 to receive entry question(std txt rate)T&Cs apply 08452810075over18s',
    'U dun say so early hor... U c already then say...',
    'Nah I dont think he goes to usf, he lives around here though',
    'FreeMsg Hey there darling its been 3 weeks now and no word back! Id like some fun you up for it still? Tb ok! XxX std chgs to send, 1.50 to rcv',
]

#The SDNController class is used to controll the flow of the network by containing logic for safety mechanisms
class SDNController:
    def __init__(self, env, model):
        self.env = env
        self.classifier = Classifier(model)
        self.routing_table = {}
    
    #add a connection to the network
    def add_flow(self, sender, receiver):
        self.routing_table[sender] = receiver
    
    #handle packet from the switch 
    def packet_from_switch(self, switch, sender, receiver, packet):

        #if a connection is not pressent on the table there is anothorized access and the packet is dropped
        if self.routing_table[sender] != receiver.ip:
            print(f"{self.env.now}: Anothorized communication from {sender}, packet dropped.")

        #if the packet contains malisious information then it is dropped and the user is classified as malicious else it is forwarded to its destination
        if self.classifier.classify(packet):
            print(f"{self.env.now}: Malicious packet from {sender} dropped.")

            if not ((sender in switch.blacklist)):
                switch.blacklist.append(sender)
                print(f"{self.env.now}: Sender {sender} appended on blacklist")
        else:
            switch.forward_packet(packet, receiver)

#The host class composes the users of the network
class Host:
    def __init__(self, env, ip):
        self.env = env
        self.ip = ip

    #send a packet to the switch
    def send_packet(self, packet, receiver, switch):
        switch.receive_packet(self.ip, receiver, packet)

    #receive a packet from the switch
    def receive_packet(self, packet):
        print(f"{self.env.now}: {self.ip} received packet: {packet}")

#The switch class is used to redirect the messages that flow through the network
class Switch:
    def __init__(self, env, controller):
        self.env = env
        self.controller = controller
        self.blacklist = []

    #receive a packet from host and pass it to the SDNController for handling
    def receive_packet(self, sender, receiver, packet):
        #if user is not classified as malicious based on previous behavior send the message
        if sender in self.blacklist:
            print(f"{self.env.now}: Untrusted sender {sender} tried to communicate with {receiver.ip}. Packet dropped.")
        else:
            self.controller.packet_from_switch(self, sender, receiver, packet)

    #if everything is good forward the message
    def forward_packet(self, packet, receiver):
        self.send_packet(packet, receiver)
        print(f"{self.env.now}: Packet forwarded.")
    
    def send_packet(self, packet, receiver):
        receiver.receive_packet(packet)

#The classifier class is used to classificate the messages to malicous or not
class Classifier:
    def __init__(self, model):
        self.model = model

    def classify(self, packet):
        new_message = packet['payload']
        new_message = re.sub('[^a-zA-Z]', ' ', new_message)
        new_message = new_message.lower()
        new_message = new_message.split()
        new_message = [ps.stem(word) for word in new_message if not word in stopwords.words('english')]
        new_message = ' '.join(new_message)

        # convert the preprocessed message into a feature vector
        new_message = cv.transform([new_message]).toarray()

        # make the prediction
        result = self.model.predict(new_message)[0]

        return result

#generate a random message from messages_array
def generate_packet():
    random_message = random.choice(messages_array)
    packet = {'payload': random_message}
    return packet

if __name__ == '__main__':
    env = simpy.Environment()

    #create the hosts
    host1 = Host(env, "192.168.0.1")
    host3 = Host(env, "192.168.0.3")
    host4 = Host(env, "192.168.0.4")
    host2 = Host(env, "192.168.0.2")

    #import the classification model
    model = joblib.load('model.pkl')
    #create the controller
    controller = SDNController(env, model)

    #create the switch for the network
    switch = Switch(env, controller)

    #add the network flows
    controller.add_flow(host1.ip, host2.ip)
    controller.add_flow(host3.ip, host2.ip)
    controller.add_flow(host4.ip, host2.ip)

    # for message classification mutation
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
            packet = generate_packet()
            sender = random.choice(terminals)
            sender.send_packet(packet, receiver, switch)
            yield env.timeout(1)

    terminals = [host1,host3,host4]

    # start the simulation process
    env.process(send_packets(env, terminals, host2, switch, 20))
    env.run()