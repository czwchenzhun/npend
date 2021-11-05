<a>Provides a convenient way to append numpy arrays to a file.</a><br>

<a>The NpendWriter and NpendReader classes are used to write and read numpy arrays respectively.</a>
<h3>Requirements</h3>
<ul>
	<li>numpy</li>
	<li>sip</li>
</ul>

<h3>Usage</h3>
<div style="background-color:#f9f9f9;border:2px solid #d3d3d3;">
	<pre>
    #! -*- coding:utf-8 -*-
    from npend import NpendWriter, NpendReader
    import numpy as np
    if __name__=="__main__":
        filePath="test.npd"
        nw=NpendWriter(filePath)
        arr=np.random.random((34,5,6))# Write an array that has three dimensions.
        nw.append(arr)# Keep the size of the last two dimensions the same as the data written before.
        arr=np.random.random((10,5,6))
        nw.append(arr)
        arr=np.random.random((5,6))# Write an array with two dimensions.
        nw.append(arr)
        nw.close()
        nr=NpendReader(filePath)
        arr=nr.read()# Load numpy array from file.
        print(arr.shape,arr.dtype)
	</pre>
</div>