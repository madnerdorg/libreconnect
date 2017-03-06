
from websocket import create_connection
import sys
ws = create_connection("ws://localhost:42001/")
message = ""
messsage == input("SEND:")
print(message)
ws.send(message)
ws.close()
