# -*- coding: utf-8 -*-
import pyAgrum as gum

import testUtils
from ApproxInference import Importance


def main():
  bn = gum.loadBN("data/alarm.bif")
  print("BN read")

  evs = {"HR": 1, "PAP": 2}

  m = Importance(bn, evs, epsilon=0.2, verbose=True)
  m.run(1e-2, 100)
  print("done")

  testUtils.compareApprox(m, bn, evs)
  print(m.posterior(1))


if __name__ == '__main__':
  main()
