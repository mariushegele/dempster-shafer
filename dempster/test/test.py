import unittest
import copy

from .. import BasicMeasure, accumulate

class TestDempster(unittest.TestCase):


    def test_can_do_dempster(self):
        def _equal(a, b):
            self.assertAlmostEqual(a, b, places=7)

        subjectA = 'Anna'
        subjectB = 'Bob'
        subjectC = 'Clara'

        # m1(A, C) = 0.8, m1(Omega) = 0.2
        m1 = BasicMeasure({subjectA, subjectB, subjectC})

        m1.add_entry({subjectA, subjectC}, 0.8)
        with self.assertRaises(Exception):
            m1.add_entry({subjectC, subjectA}, 0.7)

        _equal(m1.get_measure('Omega'), 0.2)
        _equal(m1.get_measure({subjectA, subjectB, subjectC}), 0.2)

        with self.subTest('Can add an alternative entry'):
            mX = copy.deepcopy(m1)
            mX.add_entry(subjectB, 0.1)
            _equal(mX.get_measure('Omega'), 0.1)
            _equal(mX.get_measure(subjectB), 0.1)

        _equal(m1.get_belief('Omega'), 1)
        _equal(m1.get_belief({subjectA, subjectC}), 0.8)

        # Doubt = Belief(Omega \ X)
        _equal(m1.get_doubt(subjectA), 0)
        _equal(m1.get_doubt(subjectB), 0.8)
        _equal(m1.get_doubt('Omega'), 0)

        _equal(m1.get_plausibility('Omega'), 1)
        _equal(m1.get_plausibility(subjectA), 1)
        _equal(m1.get_plausibility(subjectB), 0.2)


        # m2(C) = 0.6, m2(Omega) = 0.4
        m2 = BasicMeasure({subjectA, subjectB, subjectC})
        m2.add_entry(subjectC, 0.6)
        _equal(m2.get_measure('Omega'), 0.4)

        m1m2 = accumulate(m1, m2)

        self.assertIsInstance(m1m2, BasicMeasure)
        _equal(m1m2.get_belief('Omega'), 1)


        """             m1(A,C) = 0.8    m1(Om) 0.2
        m2(C) = 0.6     C = 0.48         C = 0.12
        m2(Om) = 0.4    A,C = 0.32       Om = 0.08
        """
        _equal(m1m2.get_measure(subjectA), 0)
        _equal(m1m2.get_measure({subjectA, subjectC}), 0.32)
        _equal(m1m2.get_measure(subjectC), 0.6)
        _equal(m1m2.get_measure(subjectB), 0)
        _equal(m1m2.get_measure('Omega'), 0.08)

        _equal(m1m2.get_belief(subjectA, subjectB), 0)
        _equal(m1m2.get_belief(subjectA, subjectC),
                         0.48 + 0.32 + 0.12)

        _equal(m1m2.get_plausibility(subjectA, subjectB), 0.4)
        _equal(m1m2.get_plausibility(subjectA, subjectC), 1)
        _equal(m1m2.get_plausibility('Omega'), 1)
        _equal(m1m2.get_plausibility(subjectB), 0.08)

        # can resolve conflicts
        m3 = BasicMeasure({subjectA, subjectB, subjectC})
        m3.add_entry(subjectB, 0.5)
        m1m2m3 = accumulate(m1m2, m3)

        """             m1m2(A,C)=0.32  m1m2(C)=0.6 m1m2(Om)=0.08
        m3(B)=0.5       {}=0.16         {}=0.3      B=0.04
        m3(Om)=0.5      A,C=0.16        C=0.3       Om=0.04
                        0.32            0.6         0.08
        """
        correct_factor = 1 / (1 - 0.46)
        _equal(m1m2m3.get_measure(subjectA), 0)
        _equal(m1m2m3.get_measure(subjectA, subjectC), 0.16*correct_factor)
        _equal(m1m2m3.get_measure(subjectC), 0.3*correct_factor)
        _equal(m1m2m3.get_measure(subjectB), 0.04*correct_factor)
        _equal(m1m2m3.get_measure('Omega'), 0.04*correct_factor)

        mInvalid = BasicMeasure({subjectA, subjectB}) # different domain
        mInvalid.add_entry(subjectA, 0.8)
        with self.assertRaises(Exception):
            accumulate(m1m2m3, mInvalid)
