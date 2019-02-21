import threading
import time
mutex = threading.Lock()
config = dict()
config["m"] = mutex
config["l"] = [0,0,0,0,0]

def test(index,c):
    print(c["m"].acquire(False))
    c["l"][index] = 1
    # c["m"].release()
    print(c["l"])


t1 = threading.Thread(target=test, args=(2,config))
t2 = threading.Thread(target=test, args=(1,config))

t3 = threading.Thread(target=test, args=(0,config))
t4 = threading.Thread(target=test, args=(3,config))
t1.start()

t2.start()
config["l"][4] = 2
t3.start()

t4.start()

# print(config["l"])
print("end")