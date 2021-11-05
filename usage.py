from npend import NpendWriter,NpendReader
import numpy as np

def usage1():
    filePath="test.npd"
    nw=NpendWriter(filePath)
    arr=np.random.random((34,5,6))#Write an array that has three dimensions
    nw.append(arr)
    arr=np.random.random((10,5,6))#Write an array with three dimensions, and keep the size of the last two dimensions the same as the data written before.
    nw.append(arr)
    arr=np.random.random((5,6))#Write an array with two dimensions.
    nw.append(arr)
    nw.close()
    nr=NpendReader(filePath)
    arr=nr.read()
    print(arr.shape,arr.dtype)

def usage2():
    filePath = "test2.npd"
    nw = NpendWriter(filePath)
    arr = np.random.random((34, 5, 6))
    nw.write(arr)#The write method will overwrite the original contents of the file
    nw.close()
    nr = NpendReader(filePath)
    arr = nr.read()
    print(arr.shape, arr.dtype)

if __name__=="__main__":
    usage1()