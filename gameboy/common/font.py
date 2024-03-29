import zlib
from array import array
from base64 import b64decode

'''
Terminus Font under SIL Open Font License Version 1.1
See <terminus-font.sourceforge.net>
There are totally 256 characters, each is composed of 16 bytes data.
Each bit in a byte represents a pixel. Each character is 16x8 in pixel.
'''
TERMINUS_FONT_DATA = '''
eJxtV71qJEcQbjgYLhhWikRjCd1h7gEGB2KCYQX3Dk4uGhxM4sYSGIQ4mhFs5NjZ+RHuARzY
HAwsDA6WtaJlQWJRdEqEtJFYzNDj6p/qru7Tt6u7+aaqq6uqq6t7GVO9g2IGcvZ5Nvvr99lM
Oq5WSvWPSjnOmFAAWe4j51U7thX3rOIfxvEDrxzX4rHlyFHHPo0G9/P5vX0yL6vm/fumCvL5
py9fPs2dfDr57ofLBeCSOWVAxWECy9umrTXuOs+1RvPLg3vBb9rqvmpv0GHWbYdxHLYd8ld7
p+N4uvfKR8cBPsDGAv539leAiwOAc6cuRdOcHGUNCZjplFF7YK6N7HP035GQUMZe50rlr4Ox
t7VS9VtPOw1FJnvXjGPzLmQb0t22Lrcmp20LC8DZi0BnnLzBOBFCCGW+wtD9fbm6vpYHByu5
byqiWYmc8+LkZzeuFKK8uF0sbi/QfGwv54UBzy2HBwNehClLVYrIxfZb7zkZwFQqZRgPy7Jc
+1fUteWy75eb56997+qbl5duBbw8A2dqzLDmVZZ5/WxyfNL0KssyNzUsxgAM5VUNXO8vxxU6
UHh7vSRy89yC0mXsOonYcWfAeAdZy2j0JAFGpnWC/TysL/ClruBlF+KFXqD/sVz7bvwfvFzX
m/d3t7DtY7EL8e9IRXrekfGbEK+fzs1XuQLEfnFsy8Hvd5hpvd2uF6jfIdx8M+hVK2IPHr4+
b5aeS+x3MsTXD5F/BhuZEbmeEOVdJ8n6j+gvD/FQ++YZdktZEr5Sj/0MuZYJgf7N57qdBXu6
XnT5YXxV4eDyU9ewd2DPYP1VuYOV8yrZvwRK77YX3sus1TXo82tSgOvvUtD5+s+Mtte3KYRV
d/Ljohisw17u9LNMUvsufoi7pOsPcU0yg8Z0VD01VIBfjzKpF8CwMgic2me4xDKRD74EvH8u
pZvtXagPLTcV4PJRYHzHXt4n+ejtGhOu3ZOEi1IQ/3qaH4Ci/ecIpqr1fEeYr7j+zuEp1/Tc
0F9vlizBvp4snPc97ufCtAjo65H/0Gai9YROHNWHSDhUVMRLUUac+fqx82l71L5IuLaXyKP6
KBNeRPVjrYV+pr2hHKLDBhVapjg4aK+v3YnTrtdrBX/rTYif1o9IuPU38DLJJ8gjHvKt19tb
c+O9NNSrPXGv8bwtRV3v4L7TOP+hf+jbkD8hd3BV+q//t+/nlk8OzfGpsT5360vXJ0/2n13/
MD/wyP+LW7q/gMX9tsqmzZSFtdfXtYpw2D/wraP9qOhmY6YF+sOtvvupEbAdbv/M+TTwZvnH
1CqZo43sB8DhiViLk0PPNYFX+vG37+PP5x/jz+Pf8Ye/jN0uYfhCWDw8uAfnwTBQnuo/POR+
QAI3OpaD/jBgNRkgZcEfmlAW+8v5mzdUn/NwWbQYx1Q/zrHX9+MTbRzg/Ds7o0GdndVXV2S2
q6s6Unh6YpFDQJ6e4vGoj3LUx/Goj9FFciHieI08iS9eBu9uiI+MJ/H6iOLx3h5mK0lwslzM
53tMEFy22CbYS5COM/i4hB6x/GgJ/Lb6x9+JmN2MXRedf4qep6qDCyY5nwCn5hdSOI+N9vLZ
m7CxTiyBbmYg3e9J3WxWqz6+D+sD9NHytuDp+S3paZrlUt/nZe39nYJvXT0N6n18H1Dpjdn+
vsAe5a7PnrvrNvLJ4WHaDTTW6/NgDnTpDxZokvC10D+PWIqyTN6F0RN7GV6Iyp3/l6StGHvg
n4xHS4NvZtH4Hyfwd5s=
'''


def create_font_buffer(dark_mode: bool = False):
    blob = TERMINUS_FONT_DATA.strip().replace('\n', '').encode()
    font = zlib.decompress(b64decode(blob))
    front, back = (0x0, 0xFFFFFFFF) if dark_mode else (0xFFFFFFFF, 0x0)
    colors = array('I', [front] * (256 * 16 * 8))
    for index, b in enumerate(font):
        for bit in range(8):
            if (0x80 >> bit) & b:
                colors[index * 8 + bit] = back
    return colors
