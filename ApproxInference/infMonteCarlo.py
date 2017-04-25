# -*- coding: utf-8 -*-
import pyAgrum as gum

from . import utils
from .infGenericSampler import GenericSamplerInference
from .probabilityEstimator import ProbabilityEstimator


class MonteCarlo(GenericSamplerInference):
  def __init__(self, bn, evs, verbose=True):
    super().__init__(bn, evs, verbose)
    self._nbrReject = 0
    self._nbr = 0

  def multipleRound(self, size=1000):
    estimators = {i: ProbabilityEstimator(self._bn.variable(i))
                  for i in self._bn.ids()
                  if self._bn.variable(i).name() not in self._evs}

    def oneRound():
      self._nbr += 1
      currentPotentials = {}
      proba = {}
      for i in self._bn.topologicalOrder():
        name = self._bn.variable(i).name()
        q = gum.Potential(self._bn.cpt(i))
        for j in self._bn.parents(i):
          q *= currentPotentials[j]
        q = q.margSumIn([name])
        v, currentPotentials[i] = utils.draw(q)
        if name in self._evs:
          if v != self._evs[name]:
            self._nbrReject += 1
            return False
        else:
          proba[i] = q
      for i in proba.keys():
        estimators[i].add(currentPotentials[i])
      return True

    for i in range(size):
      while not oneRound():
        pass
    return estimators

  def run(self, epsilon=1e-2, size=1000):
    """
    :rtype: void
    """
    self._nbrReject = 0
    self._nbr = 0
    print("Looping")
    while True:
      for node_id, estimator in self.multipleRound(size).items():
        self._estimators[node_id] += estimator

        argX, x = max([(i, self._estimators[i].confidence()) for i in self._estimators.keys()], key=lambda x: x[1])

      if self._verbose:
        print("confidence : {:12.9f} ({})".format(x, self._bn.variable(argX).name()))
        print("    Reject : {:8.4f}%".format(100 * self._nbrReject / self._nbr))

      if x < epsilon:
        break
