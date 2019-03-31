import pygpu
import os

os.environ['DEVICE'] = "cuda"
pygpu.test()