from core.pose import Pose
import QuickCheck as QC

import unittest
import numpy as np
import math
from sys import version_info
if version_info[0] < 3:
    from itertools import izip
else:
    izip = zip


def poses():
    for x, y, theta in izip(QC.floats(low=-100, high=100),
                            QC.floats(low=-100, high=100),
                            QC.floats(low=-math.pi, high=2*math.pi)):
        yield Pose(x, y, theta)


class testPose(unittest.TestCase):
    """Pose construction and arithmetic"""

    def test_accessors(self):
        """X, Y and Theta can be accessed as fields"""
        p = Pose()
        self.assertEqual(p.x, 0.0)
        self.assertEqual(p.y, 0.0)
        self.assertEqual(p.theta, 0.0)

    def test_simple_construction(self):
        """X, Y, Theta construction works"""
        p = Pose(1, 2, 3)
        self.assertEqual(p.x, 1.0)
        self.assertEqual(p.y, 2.0)
        self.assertEqual(p.theta, 3.0)

    def test_list(self):
        """Pose available as list"""
        p = Pose(1, 2, 3)
        self.assertEqual(p.get_list(), [1.0, 2.0, 3.0])
        self.assertEqual(p.get_list(), list(p))

    def test_advanced_construction(self):
        """Keyword-based construction works"""
        p = Pose(x=4, y=6, theta=8)
        self.assertEqual(p.get_list(), [4.0, 6.0, 8.0])

        p = Pose(x=4, y=6)
        self.assertEqual(p.get_list(), [4.0, 6.0, 0.0])

        p = Pose(x=4, theta=6)
        self.assertEqual(p.get_list(), [4.0, 0.0, 6.0])

        p = Pose(theta=6, y=4)
        self.assertEqual(p.get_list(), [0.0, 4.0, 6.0])

        p = Pose([1, 2, 3])
        self.assertEqual(p.get_list(), [1.0, 2.0, 3.0])

        p = Pose([1, 2, 3], theta=6)
        self.assertEqual(p.get_list(), [1.0, 2.0, 6.0])

        p = Pose([1, 2, 3], y=7)
        self.assertEqual(p.get_list(), [1.0, 7.0, 3.0])

        p = Pose([1, 2, 3], x=6, y=7)
        self.assertEqual(p.get_list(), [6.0, 7.0, 3.0])

        q = Pose(p, x=4)
        self.assertEqual(q.get_list(), [4.0, 7.0, 3.0])

        q = Pose(p, theta=4)
        self.assertEqual(q.get_list(), [6.0, 7.0, 4.0])

        p = Pose(1, 2, 3, theta=4)
        self.assertEqual(p.get_list(), [1.0, 2.0, 4.0])

    def test_bad_construction(self):
        """Construction fails on weird arguments"""
        # Too many arguments
        self.assertRaises(ValueError, lambda: Pose(1, 2, 3, 4))
        self.assertRaises(ValueError, lambda: Pose([1, 2, 3, 4]))
        self.assertRaises(ValueError, lambda: Pose([1, 2, 3], 4))

        # Wrong keyword arguments
        self.assertRaises(ValueError, lambda: Pose(1, r=3, i_wear_a_hat=9))
        self.assertRaises(ValueError, lambda: Pose([1, 3, 4], r=3))

        # iterator too short
        self.assertRaises(ValueError, lambda: Pose([1, 3]))
        self.assertRaises(ValueError, lambda: Pose([1, 3], 4))

        # complex x
        self.assertRaises(TypeError, lambda: Pose(3+2j, 3, 4))
        self.assertRaises(TypeError, lambda: Pose(3, 4, x=3+2j))

        # string x
        self.assertRaises(ValueError, lambda: Pose(3, "zero", 4))
        # the following works:
        # self.assertRaises(ValueError, lambda: Pose(["1",3,math.pi],y="4.5"))

    def test_floats(self):
        """X, Y and Theta are floats"""
        p = Pose(1, 2, 3)
        self.assertIsInstance(p.x, float)
        self.assertIsInstance(p.y, float)
        self.assertIsInstance(p.theta, float)

        p = Pose(x=1, y=2, theta=3)
        self.assertIsInstance(p.x, float)
        self.assertIsInstance(p.y, float)
        self.assertIsInstance(p.theta, float)

        p = Pose([1, 2, 3])
        self.assertIsInstance(p.x, float)
        self.assertIsInstance(p.y, float)
        self.assertIsInstance(p.theta, float)

        p = Pose([1, 2, 3], x=1, y=2, theta=3)
        self.assertIsInstance(p.x, float)
        self.assertIsInstance(p.y, float)
        self.assertIsInstance(p.theta, float)

        p = Pose(p)
        self.assertIsInstance(p.x, float)
        self.assertIsInstance(p.y, float)
        self.assertIsInstance(p.theta, float)

        p = Pose(p, x=1, y=2, theta=3)
        self.assertIsInstance(p.x, float)
        self.assertIsInstance(p.y, float)
        self.assertIsInstance(p.theta, float)

    def test_transformation(self):
        """Transformation matrix calculated correctly"""
        tm = Pose(7, 4, 0.7).get_transformation()
        self.assertAlmostEqual(tm[0, 0], tm[1, 1])
        self.assertAlmostEqual(tm[0, 1], -tm[1, 0])
        self.assertAlmostEqual(tm[0, 0]*tm[1, 1]-tm[0, 1]*tm[1, 0], 1)

        self.assertAlmostEqual(np.arccos(tm[0, 0]), 0.7)

        self.assertEqual(list(tm[:, 2]), [7.0, 4.0, 1.0])
        self.assertEqual(tm[2, 0], 0)
        self.assertEqual(tm[2, 1], 0)

    def test_equality(self):
        """Poses can be compared"""
        p = Pose(1./7, 974./13, 2*3.1415926/3)
        # Far away integers
        self.assertNotEqual(p, Pose(1, 2, 3))
        # Truly equal floats
        self.assertEqual(p, Pose(14./98, 75-1./13, 3.1415926*16./24))
        # Close floats
        self.assertNotEqual(p, Pose(p, x=116./819))
        self.assertNotEqual(p, Pose(p, theta=0.666667*355./113))
        self.assertNotEqual(p, Pose(p, y=74.923))
        # Pathological cases
        self.assertEqual(Pose(), Pose())
        self.assertEqual(Pose(), Pose(theta=2*math.pi))
        self.assertEqual(Pose(theta=-math.pi), Pose(theta=math.pi))

        # Comparison with other types
        self.assertNotEqual(Pose(), 0)
        self.assertFalse(Pose() == 0)
        self.assertNotEqual(Pose(), [0, 0, 0])

    def test_repr(self):
        """repr() can be reconstructed with eval()"""
        p = Pose(2.3, 5.6, 9.0)
        self.assertEqual(eval(repr(p)), p)

    def test_str(self):
        """String conversion is readable"""
        import re
        p = Pose(2.3, 4.5, 9.234)
        m = re.match(r'\((?P<x>[^, ]+),(?P<y>[^\)]+)\) (?P<theta>.*)$',
                     str(p))
        self.assertIsNotNone(m)
        self.assertAlmostEqual(float(m.group('x')), p.x)
        self.assertAlmostEqual(float(m.group('y')), p.y)
        self.assertAlmostEqual(float(m.group('theta')), p.theta)

    def test_shift_faults(self):
        """Shifts only work with Poses"""
        a = Pose(1, 2, 0.5)
        self.assertRaises(TypeError, lambda x: a >> x, 2)
        self.assertRaises(TypeError, lambda x: a << x, 2)

    @QC.forall(tries=100, a=poses(), b=poses())
    def test_shifts(self, a, b):
        """Shifts are reversible and predictable"""
        self.assertEqual(a >> Pose(0, 0, 0), a)
        self.assertEqual(a << Pose(0, 0, 0), a)

        self.assertEqual((a >> b) << b, a)
        self.assertEqual((a << b) >> b, a)
        self.assertEqual((b >> a) << a, b)
        self.assertEqual((b << a) >> a, b)

        self.assertEqual(a >> Pose(1, 1, 0),
                         Pose(a, x=a.x+1, y=a.y+1))
        self.assertEqual(a >> Pose(0, 0, math.pi/2),
                         Pose(-a.y, a.x, a.theta+math.pi/2))
        self.assertEqual(a >> Pose(0, 0, math.pi/2) << Pose(0, 0, -math.pi/2),
                         Pose(-a.x, -a.y, a.theta+math.pi))
