import multiprocessing

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
    q = multiprocessing.Queue()
    q.put(data)
    data.add()
    print('mian c', data.c)
    p1 = multiprocessing.Process(target=my_add, args=(q, ))
    
    p2 = multiprocessing.Process(target=my_add, args=(q, ))
    print(data.add())
    p1.start()
    p2.start()