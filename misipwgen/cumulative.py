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

    def weight_at(self, index):
        return self.cumulative[index]

    def invert(self, weight):
        """ invert function """
        for j, w in self.cumulative.items():
            if w < weight:
                continue
            else:
                break
        return j
