import threading
import queue

class Data:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.c = a + b

    def add(self):
        self.c = self.c + self.a + self.b
        return self.c

def my_add(q):
    data = q.get()
    print('child', data.add())
    q.put(data)
    return

if __name__ == '__main__':
    a=1
    b=2
    data = Data(a, b)
    q = queue.Queue()
    q.put(data)
    t1 = threading.Thread(target=my_add, args=(q, ))
    t1.start()
    t2 = threading.Thread(target=my_add, args=(q, ))
    t2.start()
    print(data.add())