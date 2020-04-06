from itertools import chain, combinations
from collections import defaultdict

def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))


class BasicMeasure():

    def validate_set(self, in_set):
        if isinstance(in_set, str):
            in_set = {in_set}
        try:
            out_set = frozenset(in_set)
            return out_set
        except Exception as e:
            raise Exception("Entry Set must be a set of unique values", e)

    def __init__(self, entry_domain:set):
        self.entry_domain = self.validate_set(entry_domain)
        self.powerset = powerset(self.entry_domain)

        self.measures = {frozenset(entry): 0 for entry in self.powerset}
        self.measures[self.entry_domain] = 1 # Omega


    def add_entry(self, entry:set, value:float):
        entry = self.validate_set(entry)

        if entry == self.entry_domain:
            raise Exception("Don't set Omega: updated automatically")

        if self.measures[entry] != 0:
            raise Exception("Entry measure added twice")

        if not (value >= 0 and value <= 1):
            raise Exception("Value must be between 0 and 1")

        self.measures[entry] = value
        prev = float(self.measures[self.entry_domain])
        self.measures[self.entry_domain] = 1 - float(sum(self.measures.values()) - prev)

    def args_to_set(self, *args):
        if len(args) == 0:
            raise Exception("No entry provided")
        if len(args) == 1:
            if args[0] == "Omega":
                return self.entry_domain
            else:
                return self.validate_set(args[0])
        else:
            return self.validate_set(args)

    def get_measures(self):
        return self.measures

    def get_measure(self, *args):
        entry = self.args_to_set(*args)
        return self.measures[entry]

    def get_belief(self, *args):
        entry = self.args_to_set(*args)
        value_gen = (m for e, m in self.measures.items()
            if e.issubset(entry))
        return sum(value_gen)

    def get_doubt(self, *args):
        entry = self.args_to_set(*args)
        domain_without_entry = self.entry_domain - entry
        return self.get_belief(domain_without_entry)

    def get_plausibility(self, *args):
        entry = self.args_to_set(*args)
        value_gen = (m for e, m in self.measures.items()
            if e.intersection(entry))

        return sum(value_gen)

def accumulate(m1:BasicMeasure, m2:BasicMeasure):
    if m1.entry_domain != m2.entry_domain:
        raise Exception("Can not accumulate two basic measures"
                        " with different entry domain: ",
                        m1.entry_domain,
                        m2.entry_domain)

    m1m2 = BasicMeasure(m1.entry_domain)
    m1m2_measures = defaultdict(float)
    conflict_sum = 0

    for m1_entry, m1_measure in m1.get_measures().items():
        if m1_measure == 0:
            continue
        for m2_entry, m2_measure in m2.get_measures().items():
            if m2_measure == 0:
                continue

            intersect = m1_entry.intersection(m2_entry)
            if intersect:
                if intersect != m1.entry_domain: # Omega, update automatically
                    m1m2_measures[intersect] += m1_measure * m2_measure
            else: # conflict
                conflict_sum += m1_measure * m2_measure

    def _resolve_conflict(measure):
        return measure / ( 1 - conflict_sum)

    for entry, measure in m1m2_measures.items():
        m1m2.add_entry(entry, _resolve_conflict(measure))
    return m1m2
