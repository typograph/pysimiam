# -*- coding:utf-8 -*-
# This code was taken from the pygame repository on 02.09.2014
# and modified to fit our version of Rect
#

# import QuickCheck as QC

import unittest
from core.rect import Rect


class RectTypeTest(unittest.TestCase):
    """pygame Rects"""

    def testConstructionXYWidthHeight(self):
        """X, Y, W, H construction"""
        r = Rect((1, 2, 3, 4))
        self.assertEqual(1, r.left)
        self.assertEqual(2, r.bottom)
        self.assertEqual(3, r.width)
        self.assertEqual(4, r.height)

    def testConstructionWidthHeight(self):
        """W, H construction"""
        r = Rect((3, 4))
        self.assertEqual(0, r.left)
        self.assertEqual(0, r.bottom)
        self.assertEqual(3, r.width)
        self.assertEqual(4, r.height)

    def testCalculatedAttributes(self):
        """Calculated attributes"""
        r = Rect((1, 2, 3, 4))

        self.assertEqual(r.left+r.width, r.right)
        self.assertEqual(r.bottom+r.height, r.top)
        self.assertEqual((r.left, r.bottom), r.bottomleft)
        self.assertEqual((r.right, r.bottom), r.bottomright)
        self.assertEqual((r.left, r.top), r.topleft)
        self.assertEqual((r.right, r.top), r.topright)

        midx = r.left + r.width / 2.0
        midy = r.bottom + r.height / 2.0

        self.assertEqual(midx, r.center[0])
        self.assertEqual(midy, r.center[1])
        self.assertEqual((r.center[0], r.center[1]), r.center)

    #def test_normalize(self):
        #r = Rect((1, 2, -3, -6))
        #r2 = Rect(r)
        #r2.normalize()
        #self.assertTrue(r2.width >= 0)
        #self.assertTrue(r2.height >= 0)
        #self.assertEqual((abs(r.width),abs(r.height)), r2.size)
        #self.assertEqual((-2,-4), r2.bottomleft)

    def test_left(self):
        """Changing the left attribute moves the rect and does not change
           the rect's width
        """
        r = Rect((1, 2, 3, 4))
        new_left = 10

        r.left = new_left
        self.assertEqual(new_left, r.left)
        self.assertEqual(Rect((new_left, 2, 3, 4)), r)

    def test_right(self):
        """Changing the right attribute moves the rect and does not change
           the rect's width
        """
        r = Rect((1, 2, 3, 4))
        new_right = r.right + 20
        expected_left = r.left + 20
        old_width = r.width

        r.right = new_right
        self.assertEqual(new_right, r.right)
        self.assertEqual(expected_left, r.left)
        self.assertEqual(old_width, r.width)

    def test_top(self):
        """Changing the top attribute moves the rect and does not change
           the rect's width
        """
        r = Rect((1, 2, 3, 4))
        new_top = 10

        r.bottom = new_top
        self.assertEqual(Rect((1, new_top, 3, 4)), r)
        self.assertEqual(new_top, r.bottom)

    def test_bottom(self):
        """Changing the bottom attribute moves the rect and does not change
           the rect's height
        """
        r = Rect((1, 2, 3, 4))
        new_bottom = r.top + 20
        expected_top = r.bottom + 20
        old_height = r.height

        r.top = new_bottom
        self.assertEqual(new_bottom, r.top)
        self.assertEqual(expected_top, r.bottom)
        self.assertEqual(old_height, r.height)

    def test_topleft(self):
        """Changing the topleft attribute moves the rect and does not change
           the rect's size
        """
        r = Rect((1, 2, 3, 4))
        new_topleft = (r.left+20, r.bottom+30)
        old_width = r.width
        old_height = r.height

        r.bottomleft = new_topleft
        self.assertEqual(new_topleft, r.bottomleft)
        self.assertEqual(old_width, r.width)
        self.assertEqual(old_height, r.height)

    def test_bottomleft(self):
        """Changing the bottomleft attribute moves the rect and does not change
           the rect's size
        """
        r = Rect((1, 2, 3, 4))
        new_bottomleft = (r.left+20, r.top+30)
        expected_topleft = (r.left+20, r.bottom+30)
        old_width = r.width
        old_height = r.height

        r.topleft = new_bottomleft
        self.assertEqual(new_bottomleft, r.topleft)
        self.assertEqual(expected_topleft, r.bottomleft)
        self.assertEqual(old_width, r.width)
        self.assertEqual(old_height, r.height)

    def test_topright(self):
        """Changing the bottomleft attribute moves the rect and does not change
           the rect's size
        """
        r = Rect((1, 2, 3, 4))
        new_topright = (r.right+20, r.bottom+30)
        expected_topleft = (r.left+20, r.bottom+30)
        old_width = r.width
        old_height = r.height

        r.bottomright = new_topright
        self.assertEqual(new_topright, r.bottomright)
        self.assertEqual(expected_topleft, r.bottomleft)
        self.assertEqual(old_width, r.width)
        self.assertEqual(old_height, r.height)

    def test_bottomright(self):
        """Changing the bottomright attribute moves the rect
           and does not change the rect's size
        """
        r = Rect((1, 2, 3, 4))
        new_bottomright = (r.right+20, r.top+30)
        expected_topleft = (r.left+20, r.bottom+30)
        old_width = r.width
        old_height = r.height

        r.topright = new_bottomright
        self.assertEqual(new_bottomright, r.topright)
        self.assertEqual(expected_topleft, r.bottomleft)
        self.assertEqual(old_width, r.width)
        self.assertEqual(old_height, r.height)

    def test_center(self):
        """Changing the center attribute moves the rect and does not change
           the rect's size
        """
        r = Rect((1, 2, 3, 4))
        new_center = (r.center[0]+20, r.center[1]+30)
        expected_topleft = (r.left+20, r.bottom+30)
        old_width = r.width
        old_height = r.height

        r.center = new_center
        self.assertEqual(new_center, r.center)
        self.assertEqual(expected_topleft, r.bottomleft)
        self.assertEqual(old_width, r.width)
        self.assertEqual(old_height, r.height)

    def test_width(self):
        "Changing the width resizes the rect from the top-left corner"
        r = Rect((1, 2, 3, 4))
        new_width = 10
        old_topleft = r.bottomleft
        old_height = r.height

        r.width = new_width
        self.assertEqual(new_width, r.width)
        self.assertEqual(old_height, r.height)
        self.assertEqual(old_topleft, r.bottomleft)

    def test_height(self):
        "Changing the height resizes the rect from the top-left corner"
        r = Rect((1, 2, 3, 4))
        new_height = 10
        old_topleft = r.bottomleft
        old_width = r.width

        r.height = new_height
        self.assertEqual(new_height, r.height)
        self.assertEqual(old_width, r.width)
        self.assertEqual(old_topleft, r.bottomleft)

    def test_size(self):
        "Changing the size resizes the rect from the top-left corner"
        r = Rect((1, 2, 3, 4))
        new_size = (10, 20)
        old_topleft = r.bottomleft

        r.size = new_size
        self.assertEqual(new_size, r.size)
        self.assertEqual(old_topleft, r.bottomleft)

    def test_contains(self):
        """Containment works"""
        r = Rect((1, 2, 3, 4))

        self.assertTrue(r.contains(Rect((2, 3, 1, 1))),
                        "r does not contain Rect((2,3,1,1))")
        self.assertTrue(r.contains(Rect(r)),
                        "r does not contain the same rect as itself")
        self.assertTrue(r.contains(Rect((2, 3, 0, 0))),
                        "r does not contain an empty rect within its bounds")
        self.assertFalse(r.contains(Rect((0, 0, 1, 2))),
                         "r contains Rect((0,0,1,2))")
        self.assertFalse(r.contains(Rect((4, 6, 1, 1))),
                         "r contains Rect((4,6,1,1))")
        self.assertTrue(r.contains(Rect((4, 6, 0, 0))),
                        "r contains Rect((4,6,0,0))")

    def test_collidepoint(self):
        """Collision with a point"""
        r = Rect((1, 2, 3, 4))

        self.assertTrue(r.collidepoint((r.left, r.bottom)),
                        "r does not collide with point (left,top)")
        self.assertFalse(r.collidepoint((r.left-1, r.bottom)),
                         "r collides with point (left-1,top)")
        self.assertFalse(r.collidepoint((r.left, r.bottom-1)),
                         "r collides with point (left,top-1)")
        self.assertFalse(r.collidepoint((r.left-1, r.bottom-1)),
                         "r collides with point (left-1,top-1)")

        self.assertTrue(r.collidepoint((r.right-1, r.top-1)),
                        "r does not collide with point (right-1,bottom-1)")
        self.assertTrue(r.collidepoint((r.right, r.top)),
                        "r collides with point (right,bottom)")
        self.assertTrue(r.collidepoint((r.right-1, r.top)),
                        "r collides with point (right-1,bottom)")
        self.assertTrue(r.collidepoint((r.right, r.top-1)),
                        "r collides with point (right,bottom-1)")

    def test_intersection(self):
        """Rect intersection"""
        r1 = Rect((1, 2, 3, 4))
        self.assertEqual(Rect((1, 2, 2, 2)),
                         r1.intersection(Rect((0, 0, 3, 4))))
        self.assertEqual(Rect((2, 2, 2, 4)),
                         r1.intersection(Rect((2, 2, 10, 20))))
        self.assertEqual(Rect((2, 3, 1, 2)),
                         r1.intersection(Rect((2, 3, 1, 2))))
        self.assertIsNone(r1.intersection(Rect((20, 30, 5, 6))))
        self.assertEqual(r1, r1.intersection(Rect(r1)),
                         "r1 does not clip an identical rect to itself")

    def test_add(self):
        """Rect addition"""
        r1 = Rect((1, 1, 1, 2))
        r2 = Rect((-2, -2, 1, 2))
        self.assertEqual(Rect((-2, -2, 4, 5)), r1 + r2)

    def test_add_ip(self):
        """Rect destructive addition"""
        r1 = Rect((1, 1, 1, 2))
        r2 = Rect((-2, -2, 1, 2))
        r1.add(r2)
        self.assertEqual(Rect((-2, -2, 4, 5)), r1)

    def test_sum(self):
        """Rect sum"""
        r1 = Rect((0, 0, 1, 1))
        r2 = Rect((-2, -2, 1, 1))
        r3 = Rect((2, 2, 1, 1))

        r4 = Rect.sum([r1, r2, r3])
        self.assertEqual(Rect((-2, -2, 5, 5)), r4)

    #def testEquals(self):
        #""" check to see how the rect uses __eq__
        #"""
        #r1 = Rect((1,2,3,4))
        #r2 = Rect((10,20,30,40))
        #r3 = (10,20,30,40)
        #r4 = Rect((10,20,30,40))

        #class foo (Rect):
            #def __eq__(self,other):
                #return id(self) == id(other)
            #def __ne__(self,other):
                #return id(self) != id(other)

        #class foo2 (Rect):
            #pass

        #r5 = foo((10,20,30,40))
        #r6 = foo2((10,20,30,40))

        #self.assertNotEqual(r5, r2)

        ## because we define equality differently for this subclass.
        #self.assertEqual(r6, r2)


        #rect_list = [r1,r2,r3,r4,r6]

        ## see if we can remove 4 of these.
        #rect_list.remove(r2)
        #rect_list.remove(r2)
        #rect_list.remove(r2)
        #rect_list.remove(r2)
        #self.assertRaises(ValueError, rect_list.remove, r2)

if __name__ == '__main__':
    unittest.main()
