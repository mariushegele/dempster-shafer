"""General functions for Dempster-Shafer theory

Classes:
    BasicMeasure: also called "mass" (dt. Basismaß)
            can be used to determine a belief, plausibility
            can be accumulated with other basic measures

Functions:
    accumulate: create a new basic measure from two basic measures
        using Dempster's rule of combination
"""

from itertools import chain, combinations
from collections import defaultdict

def powerset(iterable):
    """Returns the power set of values for any iterable.
    e.g. powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))

def process_set(in_set):
    """Check an incoming set, list or tuple of values,
    and try to convert it to a frozenset.
    """
    if isinstance(in_set, str):
        in_set = {in_set}
    try:
        out_set = frozenset(in_set)
        return out_set
    except Exception as e:
        raise Exception("Entry Set must be a set of unique values", e)


class BasicMeasure():
    """
    A class that can be used to define a basic measure / mass (dt. Basismaß)
        e.g. m1(Alive) = 0.6, m1(Dead) = 0.3, m1(Omega) = 0.1

    Attributes:
        entry_domain (frozenset): the domain of possible entries,
            where each entry is a string,
            e.g. {'Alive', 'Dead'}
        measures (dict): A dictionary mapping entry sets to measures / mass,
            e.g. {{'Alive', 'Dead'}: 0.1, ...}
    """

    def __init__(self, entry_domain):
        """Constructor of BasicMeasure.
        Initializes the measures for the power set of all possible values.

        Parameters:
            entry_domain (iterable): all possible entries
        """
        self.entry_domain = process_set(entry_domain)

        self.measures = {frozenset(entry): 0 for entry
                         in powerset(self.entry_domain)}
        self.measures[self.entry_domain] = 1 # Omega


    def add_entry(self, entry, value: float):
        """Add a single measure for an entry.
        The Omega entry is maintained automatically
        and should not be set.

        Parameters:
            entry: single string or iterable of unique strings
            value (float): mass to assign to the entry set

        Example:
            m1 = BasicMeasure({'Alive', 'Dead'})
            m1.add_entry('Alive', 0.6)
            m1.add_entry({'Dead'}, 0.3)

        Negative Example:
            m1 = BasicMeasure({'Alive', 'Dead'})
            m1.add_entry({'Alive', 'Dead'}, 0.1)
        """
        entry = process_set(entry)

        if entry == self.entry_domain:
            raise Exception("Don't set Omega: updated automatically")

        if self.measures[entry] != 0:
            raise Exception("Entry measure added twice")

        if not (round(value, 7) >= 0 and round(value, 7) <= 1):
            raise Exception("Value must be between 0 and 1", entry, value)

        self.measures[entry] = value
        prev = float(self.measures[self.entry_domain])
        self.measures[self.entry_domain] = 1 - float(sum(self.measures.values()) - prev)

    def args_to_set(self, *args):
        """Convenience function to enable getters to accept multiple
        string arguments and to interpret "Omega" as the entry set
        containing the entry domain.
            e.g. a = m1.get_measure('Alive', 'Dead')
                 b = m1.get_measure(Omega)
                 return a == b
        """
        if len(args) == 0:
            raise Exception("No entry provided")
        if len(args) == 1:
            if args[0] == "Omega":
                return self.entry_domain
            return process_set(args[0])
        return process_set(args)

    def get_measures(self):
        """Return a dictionary mapping all entries to their measures"""
        return self.measures

    def get_measure(self, *args):
        """Return the mass for a single entry set"""
        entry = self.args_to_set(*args)
        return self.measures[entry]

    def get_belief(self, *args):
        """Return the belief for a single entry set"""
        entry = self.args_to_set(*args)
        value_gen = (m for e, m in self.measures.items()
                     if e.issubset(entry))
        return sum(value_gen)

    def get_doubt(self, *args):
        """Return the doubt for a single entry set"""
        entry = self.args_to_set(*args)
        domain_without_entry = self.entry_domain - entry
        return self.get_belief(domain_without_entry)

    def get_plausibility(self, *args):
        """Return the plausibility for a single entry set"""
        entry = self.args_to_set(*args)
        value_gen = (m for e, m in self.measures.items()
                     if e.intersection(entry))

        return sum(value_gen)

def accumulate(m1: BasicMeasure, m2: BasicMeasure):
    """
    Accumulate to measures using Dempster's rule of combination.
    Applies conflict resolution. For example usage best regard the tests.

    Parameters:
        m1 (BasicMeasure): a basic measure of a certain entry domain
        m2 (BasicMeasure): a basic measure of the same domain

    Returns:
        m12 (BasicMeasure): a basic measure containing the accumulated values
    """
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
        return measure / (1 - conflict_sum)

    for entry, measure in m1m2_measures.items():
        m1m2.add_entry(entry, _resolve_conflict(measure))
    return m1m2
