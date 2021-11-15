from random import randint


class CumulativeDistribution:

    def __init__(self, weights):
        self.cumulative = self._build(weights)

    @staticmethod
    def _build(weights):
        res = dict()
        last_cum = 0
        for i, weight in enumerate(weights):
            last_cum = res[i] = last_cum + weight
        return res

    def random_invert(self, max_index):
        """
        Return index
        :return:
        """
        max_weight = self.cumulative[max_index]
        weight = randint(0, max_weight)
        return self._invert(weight)

    def _invert(self, weight):
        """ invert function """
        for j, w in enumerate(self.cumulative):
            if w < weight:
                continue
            else:
                break
        return j
