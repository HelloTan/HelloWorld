import os, sys, time
path = os.path.join(os.path.dirname(__file__), '../lib/')
sys.path.insert(0, path)

from thrift.transport import THttpClient
from thrift.protocol import TCompactProtocol

from Gen import LineService
from Gen.ttypes import *
#import ssl
#ssl._create_default_https_context = ssl._create_unverified_context

class Poll:

  client = None

  auth_query_path = "/api/v4/TalkService.do";
  http_query_path = "/S4";
  polling_path = "/P4";
  host = "gd2.line.naver.jp";
  port = 443;#80

  UA = "Line/7.4.7 iPad3,6 7.0.2"
  LA = "IOSIPAD 7.4.7 iPhone OS 7.0.2"

  rev = 0

  def __init__(self, authToken):
    self.transport = THttpClient.THttpClient("https://"+self.host, None, self.http_query_path)
    self.transport.path = self.auth_query_path
    self.transport.setCustomHeaders({"X-Line-Application" : self.LA,"User-Agent" : self.UA,"X-Line-Access": authToken})
    #self.protocol = TBinaryProtocol.TBinaryProtocol(self.transport);
    self.protocol = TCompactProtocol.TCompactProtocol(self.transport);
    self.client = LineService.Client(self.protocol)
    self.rev = self.client.getLastOpRevision()
    self.transport.path = self.polling_path
    self.transport.open()

  def stream(self):
    while True:
      try:
        Ops = self.client.fetchOperation(self.rev, 50)
      except EOFError:
        raise Exception("It might be wrong revision\n" + str(self.rev))

      for Op in Ops:
          # print Op.type
        if (Op.type != OpType.END_OF_OPERATION):
          self.rev = max(self.rev, Op.revision)
          return Op
