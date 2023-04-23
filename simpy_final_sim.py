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

messages_array = [
    'Go until jurong point, crazy.. Available only in bugis n great world la e buffet... Cine there got a...',
    'Ok lar... Joking wif u oni...',
    'Free entry in 2 a wkly comp to win FA Cup final tkts 21st May 2005. Text FA to 87121 to receive entry question(std txt rate)T&Cs apply 08452810075over18s',
    'U dun say so early hor... U c already then say...',
    'Nah I dont think he goes to usf, he lives around here though',
    'FreeMsg Hey there darling its been 3 weeks now and no word back! Id like some fun you up for it still? Tb ok! XxX std chgs to send, 1.50 to rcv',
]

class Host:
    def __init__(self, env, ip):
        self.env = env
        self.ip = ip

    def send_packet(self, packet, receiver, switch):
        switch.receive_packet(self.ip, receiver, packet)

    def receive_packet(self, packet):
        print(f"{self.env.now}: {self.ip} received packet: {packet}")

class Switch:
    def __init__(self, env, model):
        self.env = env
        self.classifier = Classifier(model)

    def receive_packet(self, sender, receiver, packet):
        if self.classifier.classify(packet):
            print(f"{self.env.now}: Malicious packet dropped.")
        else:
            self.forward_packet(packet, receiver)

    def forward_packet(self, packet, receiver):
        self.send_packet(packet, receiver)
        print(f"{self.env.now}: Packet forwarded.")
    
    def send_packet(self, packet, receiver):
        receiver.receive_packet(packet)

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

def generate_packet():
    random_message = random.choice(messages_array)
    packet = {'payload': random_message}
    return packet

def run_simulation(env, host1, host2, switch):
    while True:
        # generate a packet and send it from host1 to host2 through the switch
        packet = generate_packet()
        host1.send_packet(packet, host2, switch)
        yield env.timeout(1)

if __name__ == '__main__':
    env = simpy.Environment()
    host1 = Host(env, "192.168.0.1")
    host2 = Host(env, "192.168.0.2")
    model = joblib.load('model.pkl')
    switch = Switch(env, model)

    # for message classification mutation
    cv = CountVectorizer(max_features=4000)
    ps = PorterStemmer()
    # Load the corpus list
    with open('corpus.pkl', 'rb') as f:
        corpus = pickle.load(f)

    # fit the CountVectorizer again with the updated corpus
    cv.fit(corpus)

    # create a simulation process for host1 to send packets to host2 via switch
    def send_packets(env, host1, host2, switch, num_packets):
        for i in range(num_packets):
            packet = generate_packet()
            host1.send_packet(packet, host2, switch)
            yield env.timeout(1)

    # start the simulation process
    env.process(send_packets(env, host1, host2, switch, 20))
    env.run()