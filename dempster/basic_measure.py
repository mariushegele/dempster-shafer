from itertools import chain, combinations

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))

class BasicMeasure():

    def validate_set(self, in_set):
        if isinstance(in_set, str):
            return {in_set}
        try:
            out_set = frozenset(in_set)
            return out_set
        except Exception as e:
            raise Exception("Entry set must be a set of unique values", e)


    def __init__(self, entry_set:set):
        self.entry_set = self.validate_set(entry_set)
        self.powerset = powerset(self.entry_set)

        self.measures = {frozenset(entry): 0 for entry in self.powerset}
        self.measures[self.entry_set] = 1 # Omega

    def add_entry(self, entry:set, value:float):
        entry = self.validate_set(entry)

        if entry == self.entry_set:
            raise Exception("Don't set Omega: updated automatically")

        if self.measures[entry] != 0:
            raise Exception("Entry measure added twice")

        if not (value >= 0 and value <= 1):
            raise Exception("Value must be between 0 and 1")

        self.measures[entry] = value
        prev = float(self.measures[self.entry_set])
        self.measures[self.entry_set] = 1 - float(sum(self.measures.values()) - prev)

    def args_to_set(self, *args):
        if len(args) == 0:
            raise Exception("No entry provided")
        if len(args) == 1:
            if args[0] == "Omega":
                return self.entry_set
            else:
                return self.validate_set(args[0])
        else:
            return self.validate_set(args)

    def get_measure(self, *args):
        entry = self.args_to_set(*args)
        return self.measures[entry]

    def get_belief(self, *args):
        entry = self.args_to_set(*args)
        value_gen = (m for e, m in self.measures.items()
            if e.issubset(entry))
        return sum(value_gen)

    def get_plausibility(self, *args):
        entry = self.args_to_set(*args)
        value_gen = (m for e, m in self.measures.items()
            if e.intersection(entry))

        return sum(value_gen)
