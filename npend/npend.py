import numpy as np
from sip import voidptr
from npend.dataType import DataType
from os import path
import warnings

#=================
# This file customizes the write format of numpy arrays and provides a convenient way to append writes.
# The code does not check for file extensions, but it is recommended to use “.npd” as a suffix.
# The HeaderLen bytes at the beginning of the file are reserved to hold the description information of the array.
# The first byte indicates the data type, and every fourth subsequent byte indicates the dimension of a dimension.
#
# 这个文件自定义了numpy数组的写入格式,提供了方便的追加写入方式。
# 代码不会检查文件后缀名，但是建议使用“.npd”作为后缀名。
# 文件开头的HeaderLen个字节预留用于保存数组的描述信息。
# 第一个字节表示数据类型，后续的每4个表示一个维度的尺寸。
#=================

HeaderLen=65

class NpendReader:
    def __init__(self,filePath):
        """[Constructor of NpendReader. Construct an NpendReader object to read the numpy array stored in filePath.]

        Args:
            filePath ([str]): [Path to the file where the numpy array is saved.]
        """
        self.filePath=filePath
        self.fp=None
        self._shape=None
        self._dtype=None

    def shape(self):
        """[Returns the shape of the array saved in the file. This method may read the npd file to get header info.]

        Returns:
            [tuple]: [shape of the array saved in the file.]
        """
        if self._shape is None:
            self.__getHeader__()
        return self._shape

    def dtype(self):
        """[Returns the dtype of the array saved in the file. This method may read the npd file to get header info.]

        Returns:
            [str]: [dtype of the array saved in the file.]
        """
        if self._dtype is None:
            self.__getHeader__()
        return self._dtype

    def read(self):
        """[This method will read and return the numpy array saved in the npd file. The file will be closed after reading.]

        Returns:
            [numpy array]: [numpy array saved in the npd file]
        """
        shape=self.shape()
        dtype=self.dtype()
        if self.fp is None:
            self.__open__()
        arr=np.zeros(shape,dtype=dtype)
        ptr=voidptr(arr.data)
        self.fp.seek(HeaderLen)
        ptr[0:]=self.fp.read(len(ptr))[0:]
        self.__close__()
        return arr

    def __close__(self):
        if not self.fp is None:
            self.fp.close()
            self.fp=None

    def __open__(self):
        self.fp=open(self.filePath,'rb')

    def __getHeader__(self):
        if self.fp is None:
            self.__open__()
        header=self.fp.read(HeaderLen)
        self.__close__()
        idx = int.from_bytes(header[0:1], byteorder="big")
        self._dtype=DataType[idx]
        ls = []
        head = header[1:]
        N=(HeaderLen-1)//4
        for i in range(N):
            num = int.from_bytes(head[i * 4:(i + 1) * 4], byteorder="big")
            if num == 0:
                break
            ls.append(num)
        self._shape = tuple(ls)

def is_number(str):
    try:
        if str == 'NaN':
            return False
        float(str)
        return True
    except ValueError:
        return False

class NpendWriter:
    def __init__(self,filePath):
        """[Constructor of NpendWriter. Construct an NpendWriter object to write the numpy array, data will save to filePath.]

        Args:
            filePath ([str]): [Array data save path.]
        """
        self.filePath=filePath
        self.fp=None
        self.alreadyExist=path.exists(filePath)
        self.shape=None
        self.dtype=None
        if self.alreadyExist:
            nr=NpendReader(filePath)
            self.shape=nr.shape()
            self.dtype=nr.dtype()

    def __del__(self):
        if not self.fp is None:
            self.close()

    def write(self,arr):
        """[Write the numpy array. !!! Attention: The write method will overwrite the original contents of the file.]

        Args:
            arr ([numpy array]): [Array to be written.]
        """
        self.__open__('wb')
        self.__writeDontExist__(arr)

    def append(self,arr):
        """[Writing an array to a file as an append. The shape and dtype of the array should be compatible with the contents of the file.]

        Args:
            arr ([numpy array]): [Array to be written.]
        """
        if self.alreadyExist:
            if self.fp is None:
                self.__open__('r+b')  # 'ab'会强制在末尾write，也就是说在ab模式下seek方法失效
            self.__writeExist__(arr)
        else:
            if self.fp is None:
                fi=open(self.filePath,'wb')#'r+'模式在文件不存在是会抛异常
                fi.close()
                self.__open__('r+b')  # 'ab'会强制在末尾write，也就是说在ab模式下seek方法失效
            self.__writeDontExist__(arr)

    def close(self):
        """[Close the file.]
        """
        if not self.fp is None:
            self.fp.close()
            self.fp=None

    def __writeDontExist__(self,arr):
        self.fp.seek(0, 2)
        if is_number(str(arr)):
            self.shape = (1,)
        else:
            self.shape = arr.shape
        self.dtype = str(arr.dtype)
        header = self.__constructHeader__(self.dtype, self.shape)
        self.fp.write(header)
        ptr = voidptr(arr.data)
        self.fp.write(ptr[0:])
        self.fp.flush()
        self.alreadyExist = True

    def __writeExist__(self,arr):
        self.fp.seek(0,2)
        ret = self.__check__(arr)
        if ret == False:
            arr = arr.astype(self.dtype)
        ptr = voidptr(arr.data)
        self.fp.write(ptr[0:])
        shapeLs = list(self.shape)
        if len(self.shape) == len(arr.shape):
            shapeLs[0] += arr.shape[0]
        else:
            shapeLs[0] += 1
        self.shape = tuple(shapeLs)
        header = self.__constructHeader__(self.dtype, self.shape)
        self.fp.seek(0)
        self.fp.write(header)
        self.fp.flush()
        self.fp.seek(0, 2)

    def __constructHeader__(self,dtype,shape):
        for key in DataType:
            if dtype==DataType[key]:
                idx=key
                break
        header=b''
        header+=(idx).to_bytes(1,byteorder="big")
        for dim in shape:
            header+=(dim).to_bytes(4,byteorder="big")
        diff=HeaderLen-len(header)
        header+=bytes(diff)
        return header

    def __open__(self,mode):
        self.fp=open(self.filePath,mode)

    def __check__(self, arr):
        dimDiff=len(self.shape)-len(arr.shape)
        if (dimDiff == 0 and arr.shape[1:] != self.shape[1:])\
                or (dimDiff == 1 and arr.shape != self.shape[1:] \
                    or dimDiff < 0 or dimDiff > 2):
            info="The appended data does not match the original data shape in the file." + \
                 "The file is saved with a shape of {}, and the appended data has a shape of {}"
            info=info.format(str(self.shape), str(arr.shape))
            self.close()
            raise Exception(info)
        if arr.dtype!=self.dtype:
            dtype=str(arr.dtype)
            canCast=False
            ls = [DataType[i] for i in range(2, 13)]
            if dtype in ls and self.dtype in ls:
                canCast=True
            ls = [DataType[i] for i in range(13, 17)]
            if dtype in ls and self.dtype in ls:
                canCast = True
            ls = [DataType[i] for i in range(17, 20)]
            if dtype in ls and self.dtype in ls:
                canCast = True
            if canCast:
                info="{} cast to {}, there may be precision changes.".format(dtype,self.dtype)
                warnings.warn(info)
                return False
            else:
                self.close()
                raise Exception("Data type mismatch cannot convert {} to {}".format(dtype,self.dtype))
        return True