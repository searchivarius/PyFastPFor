#!/usr/bin/env python3

from pyfastpfor import *
import numpy as np
import random
import time
random.seed(0)


def oneTest(arrSize, maxVal, codecList):
    inpSmall = np.array(np.random.randint(
        0, maxVal, arrSize), dtype=np.uint32).ravel()
    inpPrefSum = np.array(inpSmall, dtype=np.uint32, copy=True).ravel()

    comp = np.zeros(2 * arrSize + 1024, dtype=np.uint32, order='C').ravel()
    unComp = np.zeros(2 * arrSize + 1024, dtype=np.uint32, order='C').ravel()

    assert (np.all(inpSmall >= 0))

    s = inpPrefSum[0]
    for i in range(arrSize):
        s = inpPrefSum[i] + s
        inpPrefSum[i] = s

    inpPrefSum.sort()

    print("Input Size: %d" % arrSize)
    print("Maximum Value: %d" % maxVal)
    print()

    diffTypeNames = {0: 'none', 1: '  d1', 2: '  d4', 3: '  d4'}

    longestNameLength = max([len(n) for n in codecList])

    for cname in codecList:
        codec = getCodec(cname)

        for diffType in range(3):

            if diffType == 0:
                inp = np.array([e for e in inpSmall], dtype=np.uint32).ravel()
            else:
                inp = np.array([e for e in inpPrefSum], dtype=np.uint32).ravel()

            if diffType == 1:
                delta1(inp, arrSize)
            elif diffType == 2:
                delta4(inp, arrSize)

            compSize = codec.encodeArray(inp, arrSize, comp, len(comp))

            t1 = time.time()
            uncompSize = codec.decodeArray(comp, compSize, unComp, len(unComp))
            t2 = time.time()

            assert (uncompSize == arrSize)
            assert (np.all(inp == unComp[0:uncompSize]))

            if np.all(inp == unComp[0:uncompSize]):
                passfail = "Pass"
            else:
                passfail = "FAIL"

            spaces = ' ' * (longestNameLength-len(cname))
            print("[%s] %s %s  DiffType: %s  Ratio: %4.2fx  Time: %6.3f ms" %
                  (cname, spaces, passfail, diffTypeNames[diffType], uncompSize/compSize, 1000*(t2-t1)))

        if diffType == 1:
            prefixSum1(inp, arrSize)
        elif diffType == 2:
            prefixSum4(inp, arrSize)

        if diffType == 0:
            assert (np.all(inp == inpSmall))
        else:
            assert (np.all(inp == inpPrefSum))


if __name__ == '__main__':

    codecList = getCodecList()

    # Be careful changing these numbers: If the array size
    # is too large there will be an integer overflow.
    arraySizes = [1, 8, 64, 1024, 1024 * 1024 * 4]
    maxValues = [256, 512, 2048]

    i = 0
    for arraySize in arraySizes:
        for maxValue in maxValues:
            print("--------------------------------------------------------------------------------")
            print("                              Test Case %d/%d" % (i, len(arraySizes)*len(maxValues)))
            print("--------------------------------------------------------------------------------")
            oneTest(arraySize, maxValue, codecList)
            print("\n")
            i += 1
