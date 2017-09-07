## 
# Here is my protocol, that asks a qusetion about NFL Football teams and request
# users to match the correct cardinal direction in the conference of the team.
# We have three packets below: a question, an answer, and a grade that gets sent

from playground.network.packet import *
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT32, STRING, BUFFER, BOOL

# This is the question the server will send back to the client 
# after receiving a request to connect.
class PacketQuestion(PacketType):
  DEFINITION_IDENTIFIER = "lab1b.Arpan_Ghosh.PacketQuestion"
  DEFINITION_VERSION = "1.0"

  FIELDS = [
	("ID", UINT32),
	("team", STRING),
	("conference", STRING),
	("data", BUFFER)
	]


# the answer packet sent back to the server
class PacketAnswer(PacketType):
  DEFINITION_IDENTIFIER = "lab1b.Arpan_Ghosh.PacketAnswer"
  DEFINITION_VERSION = "2.0"

  FIELDS = [
  ("ID", UINT32),
  ("answer", STRING)
  ]


# The server sends back a 'correct' or 'incorrect' evaluation
class PacketGrade(PacketType):
  DEFINITION_IDENTIFIER = "lab1b.Arpan_Ghosh.PacketGrade"
  DEFINITION_VERSION = "3.0"

  FIELDS = [
  ("ID", UINT32),
  ("grade", STRING)
  ]


# instantiate packet 1
packet1 = PacketQuestion()
packet1.ID = 100
packet1.team = "Baltimore Ravens"
packet1.conference = "AFC"
packet1.data = b"What cardinal division are the Ravens in?"
packet1Bytes = packet1.__serialize__()

# instantiate packet 2
packet2 = PacketAnswer()
packet2.ID = 100
packet2.answer = "North"
packet2Bytes = packet2.__serialize__()

# instantiate packet 3
packet3 = PacketGrade()
packet3.ID = 100
packet3.grade = "CORRECT"
packet3Bytes = packet3.__serialize__()

pktBytes = packet1.__serialize__() + packet2.__serialize__() + packet3.__serialize__()


## TEST DESERIALIZER
deserializer = PacketType.Deserializer()
print('Starting with {} bytes of data'.format(len(pktBytes)))
while len(pktBytes) > 0:
  chunk, pktBytes = pktBytes[:10], pktBytes[10:]
  deserializer.update(chunk)
  print('Another 10 bytes loaded into deserializer. Left={}'.format(len(pktBytes)))
  for packet in deserializer.nextPackets():
    print("got a packet!")
    if packet == packet1: print('Its packet 1!')
    elif packet == packet2: print('Its packet2!')
    elif packet == packet3: print('Its packet3!')

## UNIT TEST #!
## TEST THE RAVENS, AFC ANSWER

def basicUnitTest():
  deserializer = PacketType.Deserializer()

  p1 = PacketQuestion()
  p1.ID = 101
  p1.team = "Washington Redskins"
  p1.conference = "NFC"
  p1.data = b"What cadinal division are the Redskins in?"
  p1Bytes = p1.__serialize__()
  p1a = PacketType.Deserialize(p1Bytes)
  
  assert p1==p1a
  # or manually wth if/else statements
  if (p1==p1a):
    print("p1: assert true, these are equal")
  else:
    print("These are different.")

  p2 = PacketQuestion()
  p2.ID = 102
  p2.team = "Dallas Cowboys"
  p2.conference = "NFC"
  p2.data = b"What cardinal division are the Cowboys in?"
  p2Bytes = p2.__serialize__()
  p2aFake = PacketType.Deserialize(p1Bytes)
  p2a = PacketType.Deserialize(p2Bytes)

  if (p1==p1a):
    print("p1: assert true, these are equal")
  else:
    print("These are different.")
  
  try:
    assert True 
    assert p2 == p2a
  except AssertionError:
    print("An assertion error was caught! This is good, because these are indeed different packets")
  
  print ('p2.ID: %d' % p2a.ID) #NOTE: p2a was passed in p1Bytes, NOT p2Bytes
  print ('p1.ID: %d' % p1.ID)
  if (p2a.ID == p1.ID):
    print('These are equal!')
  else:
    print('These are not equal!')
 
  print ('p2a.team: ', str(p2a.team)) #NOTE: p2a was passed in p2Bytes
  print ('p2.team: ', str(p2.team))
  if (p2a.team == p2.team):
    print('These are equal!')
  else:
    print('These are not equal!')
  
  p3 = PacketGrade()
  p3.ID = 103
  p3.grade = "INCORECT"
  p3Bytes = p3.__serialize__()
  p3a = PacketType.Deserialize(p3Bytes)
  print ('p3a.grade: ', str(p3a.grade)) #NOTE: p3a was passed in p3Bytes
  print ('p3.grad3: ', str(p3.grade))
  if (p3a.grade == p3.grade):
    print('Good. The correct grade was given.')
  else:
    print('These are not equal!')

if __name__=="__main__":
  basicUnitTest()