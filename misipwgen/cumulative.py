from bisect import bisect_left


class CumulativeDistribution:
    def __init__(self, weights):
        # Store both a list (for fast bisect) and a dict for backward compatibility/tests
        self._cumlist = self._build_list(weights)
        self.cumulative = {i: v for i, v in enumerate(self._cumlist)}

    @staticmethod
    def _build_list(weights):
        res = []
        last_cum = 0
        for weight in weights:
            last_cum += weight
            res.append(last_cum)
        return res

    def weight_at(self, index):
        return self._cumlist[index]

    def invert(self, weight):
        """Return the smallest index with cumulative >= weight.

        Accepts weight in [1, max_weight]. Values > max map to last index.
        """
        if not self._cumlist:
            raise ValueError("Empty cumulative distribution")
        idx = bisect_left(self._cumlist, weight)
        if idx >= len(self._cumlist):
            idx = len(self._cumlist) - 1
        return idx
