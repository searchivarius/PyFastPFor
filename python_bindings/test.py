#!/usr/bin/env python3

import random
random.seed(0)

import numpy as np
from pyfastpfor import *

def oneTest(arrSize, maxVal, codecList = ["vbyte", "varintg8iu", "simdbinarypacking", "simdfastpfor256"]):
  inp = np.array(np.random.randint(0, maxVal, arrSize), dtype = np.uint32).ravel()
  # Fails when we give only arrSize + 1024 as a compressed buffer size, which is super weird,
  # because arrSize + 1024 should be more than enough
  comp = np.zeros(1 * arrSize + 1024, dtype = np.uint32, order = 'C')
  unComp = np.zeros(2 * arrSize + 1024, dtype = np.uint32, order = 'C') 

  assert(np.all(inp >= 0))

  s = inp[0]
  for i in range(arrSize):
    s = inp[i] + s
    inp[i] = s

  inp.sort()

  inpCopy = [e for e in inp]

  for diffType in range(3):
    print('Diff/delta type: %s' % ('none' if diffType == 0 else 'd1' if diffType == 1 else 'd4'))

    if diffType == 1:
      delta1(inp, arrSize)
    elif diffType == 2:
      delta4(inp, arrSize)

    for cname in codecList:
      codec = getCodec(cname)

      compSize = codec.encodeArray(inp, arrSize, comp, len(comp))
      uncompSize = codec.decodeArray(comp, compSize, unComp, len(unComp))

      print(cname, arrSize, uncompSize, np.all(inp == unComp[0:uncompSize]))

      assert(np.all(inp == unComp[0:uncompSize]))

    if diffType == 1:
      prefixSum1(inp, arrSize)
    elif diffType == 2:
      prefixSum4(inp, arrSize)

    assert(np.all(inp == inpCopy))


for t in [1, 8, 64, 1024, 1024 * 1024]:
  for maxVal in [256, 512, 2048]:
    print("Test size=%d maxVal %d" % (t, maxVal))

    oneTest(t, maxVal) 
