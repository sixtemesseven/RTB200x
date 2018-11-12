# -*- coding: utf-8 -*-
"""
Created on Sun Aug 12 20:59:15 2018

@author: sixtimesseven
"""

import cmath

referenceP = -10.15
referenceA = -8.7
measuredP = -10.20
measuredA = -11
shuntR = 366


def main():
    rVpp = dbmToVpp(referenceP)
    mVpp = dbmToVpp(measuredP)
    V1 = cmath.rect(rVpp, referenceA)
    V2 = cmath.rect(mVpp, measuredA)
    
    complexI = ((V1-V2)/shuntR)
    Xtotal = V2/complexI
    Rdut = cmath.polar(Xtotal)
    print(Rdut)

def dbmToVpp(dbm):
    return 10**((dbm-10)/20)

if __name__ == "__main__":
    main()