class SyllableCollection(list):

    def __init__(self):
        super(SyllableCollection, self).__init__()
        self.last_syllable_by_length = dict()
        self.max_syllable_length = 0

    def finalize(self):
        self.sort(key=lambda x: (x.length(), str(x)))
        self.last_syllable_by_length = dict()
        for i, syllable in enumerate(self):
            self.last_syllable_by_length[syllable.length()] = i
        self.max_syllable_length = self[-1].length()

    def last_index(self, length):
        """ return last syllables index depending  """
        length = 1 if length < 1 else self.max_syllable_length if length >= self.max_syllable_length else length
        return self.last_syllable_by_length[length]
