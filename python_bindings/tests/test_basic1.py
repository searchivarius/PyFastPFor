#!/usr/bin/env python3

import random
import time
random.seed(0)

import numpy as np
from pyfastpfor import *

def oneTest(arrSize, maxVal, codecList = ["vbyte", "varintg8iu", "simdbinarypacking", "simdfastpfor256"]):
  inpSmall = np.array(np.random.randint(0, maxVal, arrSize), dtype = np.uint32).ravel()
  inpPrefSum  = np.array(inpSmall, dtype = np.uint32, copy = True).ravel()

  comp = np.zeros(2 * arrSize + 1024, dtype = np.uint32, order = 'C').ravel()
  unComp = np.zeros(2 * arrSize + 1024, dtype = np.uint32, order = 'C').ravel()

  assert(np.all(inpSmall >= 0))

  s = inpPrefSum[0]
  for i in range(arrSize):
    s = inpPrefSum[i] + s
    inpPrefSum[i] = s

  inpPrefSum.sort()


  for diffType in range(3):
    print('Diff/delta type: %s array size: %d' % ('none' if diffType == 0 else 'd1' if diffType == 1 else 'd4', arrSize))
    if diffType == 0:
      inp = np.array([e for e in inpSmall], dtype = np.uint32).ravel()
    else:
      inp = np.array([e for e in inpPrefSum], dtype = np.uint32).ravel()

    if diffType == 1:
      delta1(inp, arrSize)
    elif diffType == 2:
      delta4(inp, arrSize)

    print('Array stat: ', np.percentile(inp, range(10,100, 10))) 

    for cname in codecList:
      codec = getCodec(cname)

      compSize = codec.encodeArray(inp, arrSize, comp, len(comp))
      print('Compressed size %d is it more compact than original? %d Compression ratio: %g' % (compSize, compSize <= arrSize, float(compSize) / arrSize))
      t1 = time.time()
      uncompSize = codec.decodeArray(comp, compSize, unComp, len(unComp))
      t2 = time.time()

      print('Decompression time %g (sec)' % (t2 - t1))

      print(cname, arrSize, uncompSize, np.all(inp == unComp[0:uncompSize]))

      assert(np.all(inp == unComp[0:uncompSize]))

    if diffType == 1:
      prefixSum1(inp, arrSize)
    elif diffType == 2:
      prefixSum4(inp, arrSize)

    if diffType == 0:
      assert(np.all(inp == inpSmall))
    else:
      assert(np.all(inp == inpPrefSum))


# Be careful in changing this numbers: if the array size
# is too large there will be an integer overflow
for t in [1, 8, 64, 1024, 1024 * 1024 * 4]:
  for maxVal in [256, 512, 2048]:
    print("Test size=%d maxVal %d" % (t, maxVal))

    oneTest(t, maxVal) 
