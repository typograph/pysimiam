# Based on work by Chandler Armstrong (omni dot armstrong at gmail dot com)


"""
polygon object
"""


from __future__ import division
from operator import mul
try:
    from functools import reduce
except ImportError:
    pass # Ignore in python2
  
try:
  xrange
except Exception:
  xrange = range

from numpy import array, cos, dot, fabs, lexsort, pi, sin, sqrt, vstack
##from pygame import Rect

##from convexhull import convexhull
# convex hull related functions 
TURN_LEFT, TURN_RIGHT, TURN_NONE = (1, -1, 0)

def _turn(i, j, k):
    global P
    _P = P
    (p_x, p_y), (q_x, q_y), (r_x, r_y) = _P[i], _P[j], _P[k]
    trn = (q_x - p_x) * (r_y - p_y) - (r_x - p_x) * (q_y - p_y)

    if trn > 0:
        return 1
    elif trn < 0:
        return -1
    return 0


def _keep_left(hull, r):
    while len(hull) > 1 and _turn(hull[-2], hull[-1], r) != TURN_LEFT: hull.pop()
    if not len(hull) or not (hull[-1] == r).all(): hull.append(r)
    return hull


def convexhull(_P):
    """
    Returns an array of the points in convex hull of P in CCW order.

    arguments: P -- a Polygon object or an numpy.array object of points
    """
    global P
    P = _P
    I = lexsort((_P[:,1],_P[:,0]))
    l = reduce(_keep_left, I, [])
    u = reduce(_keep_left, reversed(I), [])
    l.extend(u[i] for i in xrange(1, len(u) - 1))
    return array(l)


# error tolerances
_MACHEPS = pow(2, -24)
_E = _MACHEPS * 10

# utility functions
_clamp = lambda a, v, b: max(a, min(b, v))              # clamp v between a and b
_perp = lambda x_y: array([-x_y[1], x_y[0]])            # perpendicular
_prod = lambda X: reduce(mul, X)                        # product
_mag = lambda x_y: sqrt(x_y[0] * x_y[0] + x_y[1] * x_y[1])               # magnitude, or length
_normalize = lambda V: array([i / _mag(V) for i in V])  # normalize a vector
_intersect = lambda A, B: (A[1] > B[0] and B[1] > A[0]) # intersection test
_unzip = lambda zipped: zip(*zipped)                    # unzip a list of tuples

def _isbetween(o, p, q):
    # returns true if point p between points o and q
    o_x, o_y = o
    p_x, p_y = p
    q_x, q_y = q
    m = (q_y - o_y) / (q_x - o_x)
    b = o_y - (m * o_x)
    if fabs(p_y - ((m * p_x) + b)) < _MACHEPS: return True

def _line_intersect(p1, q1, p2, q2):
    """ gets an intersection point of two lines """
    x1, y1 = p1
    x2, y2 = q1
    x3, y3 = p2
    x4, y4 = q2
    
    x12 = x1 - x2
    x34 = x3 - x4
    y12 = y1 - y2
    y34 = y3 - y4

    c = x12 * y34 - y12 * x34
    
    if abs(c) > 0.001:
        # Intersection
        a = x1 * y2 - y1 * x2
        b = x3 * y4 - y3 * x4
        x = (a * x34 - b * x12) / c
        y = (a * y34 - b * y12) / c
        
        # check boundaries
        if (x - min(x1, x2) > -1e-8 and x - min(x3, x4) > -1e-8 and
            max(x1, x2) - x > -1e-8 and max(x3, x4) - x > -1e-8 and
            y - min(y1, y2) > -1e-8 and y - min(y3, y4) > -1e-8 and
            max(y1, y2) - y > -1e-8 and max(y3, y4) - y > -1e-8):
            return (x, y)
    return None


class _Support(object):
    # the support mapping of P - Q; s_P-Q
    # s_P-Q is the generic support mapping for polygons


    def __init__(self, P, Q):
        s = self._s
        self._s_P = s(P)
        self._s_Q = s(Q)
        self.M = []


    def __repr__(self): return array([m for m in self])


    def __len__(self): return len(self.M)


    def __iter__(self): return iter(p - q for p, q in self.M)


    def _s(self, C):
        # returns a function that returns the support mapping of C
        # the support mapping is the p in C such that
        #   dot(r, p) == dot(r, _s(C)(r))
        # ie, the support mapping is the p in C most in the direction of r
        return lambda r: max(dict((dot(r, p), p) for p in C).items())[1]


    def add(self, r):
        # add the value of s_P-Q(r) to self and return that value
        # NOTE: return value is always a pair of vertices from P and Q
        s_P, s_Q = self._s_P, self._s_Q
        p, q = s_P(r), s_Q(-r)
        self.M.append((p, q))
        return p - q


    def get(self, r):
        # return value of s_P-Q(r)
        # NOTE: return value is always a pair of vertices from P and Q
        s_P, s_Q = self._s_P, self._s_Q
        return s_P(r) - s_Q(-r)


    def v(self, q=array([0, 0]), i=0):
        # find the point on the convex hull of C closest to q by iteratively
        #   searching around voronoi regions
        # i is the index of the initial test edge
        # returns the point closest to q and sets self.M to be the minimum set
        #   of points in C such that q in conv(points)
        A = array(list(self))
        if len(A) > 1:
            I = convexhull(A)
            A = A[I]

        C = Polygon(A, conv=False).move(*-q)
        edges, n, P = C.edges, C.n, C.P

        if n == 1: return P[0]

        checked, inside = set(), set()
        while 1:
            checked.add(i)
            edge = edges[i]
            p = P[i]
            len2 = dot(edge, edge) # len(edge)**2
            vprj = dot(p, edge)    # p projected onto edge

            if vprj < 0:    # q lies CW of edge
                i = (i - 1) % n
                if i in checked:
                    if not i in inside:
                        self.M = [self.M[I[i]]]
                        return p - q
                    i = (i - 1) % n
                continue
            if vprj > len2: # q lies CCW of edge
                i = (i + 1) % n
                if i in checked:
                    if not i in inside:
                        p = P[i]
                        self.M = [self.M[I[i]]]
                        return p - q
                    i = (i + 1) % n
                continue

            nprj = dot(p, _perp(edge)) # p projected onto edge normal
            # perp of CCW edges will always point "outside"
            if nprj > 0: # q is "inside" the edge
                inside.add(i)
                if len(checked) == n: return q # q in C
                i = (i + 1) % n
                continue

            # q is closest to edge
            self.M = [self.M[I[i]], self.M[I[(i + 1) % n]]]
            edge_n = _normalize(edge)
            # move from p to q projected on to edge
            qprj = p - ((dot(p, edge_n)) * edge_n)
            return qprj



class Polygon(object):
    """polygon object"""


    def __init__(self, P, conv=True):
        """
        arguments:
        P -- iterable or 2d numpy.array of (x, y) points.  the constructor will
          find the convex hull of the points in CCW order; see the conv keyword
          argument for details.

        keyword arguments:
        conv -- boolean indicating if the convex hull of P should be found.
          conv is True by default.  Polygon is intended for convex polygons only
          and P must be in CCW order.  conv will ensure that P is both convex
          and in CCW.  even if P is already convex, it is recommended to leave
          conv True, unless client code can be sure that P is also in CCW order.
          CCW order is requried for certain operations.

          NOTE: the order must be with respect to a bottom left orgin; graphics
            applications typically use a topleft origin.  if your points are CCW
            with respect to a topleft origin they will be CW in a bottomleft
            origin
        """
        P = array(list(P))
        if conv: P = P[convexhull(P)]
        self.P = P
        n = len(P) # number of points
        self.n = n
        self.a = self._A() # area of polygon

        edges = [] # an edge is the vector from p to q
        for i, p in enumerate(P):
            q = P[(i + 1) % n] # x, y of next point in series
            edges.append(p - q)
        self.edges = array(edges)
        C = self.C
        # longest distance from C for all p in P
        self.rmax = sqrt(max(dot(C - p, C - p) for p in P))


    def __len__(self): return self.n


    def __getitem__(self, i): return self.P[i]

    
    def __iter__(self): return iter(self.P)


    def __repr__(self): return str(self.P)


    def __add__(self, other):
        """
        returns the minkowski sum of self and other

        arguments:
        other is a Polygon object

        returns an array of points for the results of minkowski addition

        NOTE: use the unary negation operator on other to find the so-called
          minkowski difference. eg A + (-B)
        """
        P, Q = self.P, other.P
        return array([p + q for p in P for q in Q])


    def __neg__(self): return Polygon(-self.P)


    def get_rect(self):
        """return the AABB, as a pygame rect, of the polygon"""
        X, Y = _unzip(self.P)
        x, y = min(X), min(Y)
        w, h = max(X) - x, max(Y) - y
        #return Rect(x, y, w, h)
        return (x, y, w, h)


    def move(self, x, y):
        """return a new polygon moved by x, y"""
        return Polygon([(x + p_x, y + p_y) for (p_x, p_y) in self.P])


    def move_ip(self, x, y):
        """move the polygon by x, y"""
        self.P = array([(x + p_x, y + p_y) for (p_x, p_y) in self.P])


    def collidepoint(self, x_y):
        """
        test if point x_y = (x, y) is outside, on the boundary, or inside polygon
        uses raytracing algorithm

        returns 0 if outside
        returns -1 if on boundary
        returns 1 if inside
        """
        x,y = x_y
        n, P = self.n, self.P

        # test if (x, y) on a vertex
        for p_x, p_y in P:
            if (x == p_x) and (y == p_y): return -1

        intersections = 0
        for i, p in enumerate(self.P):
            p_x, p_y = p
            q_x, q_y = P[(i + 1) % n]
            x_min, x_max = min(p_x, q_x), max(p_x, q_x)
            y_min, y_max = min(p_y, q_y), max(p_y, q_y)
            # test if (x, y) on horizontal boundary
            if (p_y == q_y) and (p_y == y) and (x > x_min) and (x < x_max):
                return -1
            if (y > y_min) and (y <= y_max) and (x <= x_max) and (p_y != q_y):
                x_inters = (((y - p_y) * (q_x - p_x)) / (q_y - p_y)) + p_x
                # test if (x, y) on non-horizontal polygon boundary
                if x_inters == x: return -1
                # test if line from (x, y) intersects boundary
                if p_x == q_x or x <= x_inters: intersections += 1

        return intersections % 2

    
    def collidepoly(self, other):
        """
        test if other polygon collides with self using seperating axis theorem
        if collision, return projections

        arguments:
        other -- a polygon object

        returns:
        an array of projections
        """
        # a projection is a vector representing the span of a polygon projected
        # onto an axis
        projections = []
        for edge in vstack((self.edges, other.edges)):
            edge = _normalize(edge)
            # the separating axis is the line perpendicular to the edge
            axis = _perp(edge)
            self_projection = self.project(axis)
            other_projection = other.project(axis)
            # if self and other do not intersect on any axis, they do not
            # intersect in space
            if not _intersect(self_projection, other_projection): return False
            # find the overlapping portion of the projections
            projection = self_projection[1] - other_projection[0]
            projections.append((axis[0] * projection, axis[1] * projection))
        return array(projections)


    def distance(self, other, r=array([0, 0])):
        """
        return distance between self and other
        uses GJK algorithm. for details see:

        Bergen, Gino Van Den. (1999). A fast and robust GJK implementation for
        collision detection of convex objects. Journal of Graphics Tools 4(2).

        arguments:
        other -- a Polygon object

        keyword arguments
        r -- initial search direction; setting r to the movement vector of
        self - other may speed convergence
        """
        P, Q = self.P, other.P
        support = _Support(P, Q) # support mapping function s_P-Q(r)
        v = support.get(r)       # initial support point
        w = support.add(-v)
        while dot(v, v) - dot(w, v) > _MACHEPS: # while w is closer to origin
            v = support.v() # closest point to origin in support points
            if len(support) == 3: return v # the origin is inside W; intersection
            w = support.add(-v)
        return v


    def raycast(self, other, r, s=array([0, 0]), self_theta=0, other_theta=0):
        """
        return the hit scalar, hit vector, and hit normal from self to other in
        direction r
        uses GJK-based raycast[1] modified to accomodate constant angular
        rotation[2][3] without needing to recompute the Minkowski Difference
        after each iteration[4].

        [1] Bergen, Gino Van Den. (2004). Ray casting against general convex
        objects with application to continuous collision detection. GDC 2005.
        retrieved from
        http://www.bulletphysics.com/ftp/pub/test/physics/papers/
        jgt04raycast.pdf
        on 6 July 2011.

        [2] Coumans, Erwin. (2005). Continuous collision detection and physics.
        retrieved from
        http://www.continuousphysics.com/
        BulletContinuousCollisionDetection.pdf
        on 18 January 2012

        [3] Mirtich, Brian Vincent. (1996). Impulse-based dynamic simulation of
        rigid body systems. PhD Thesis. University of California at Berkely.
        retrieved from
        http://www.kuffner.org/james/software/dynamics/mirtich/
        mirtichThesis.pdf
        on 18 January 2012

        [4] Behar, Evan and Jyh-Ming Lien. (2011). Dynamic Minkowski Sum of
        convex shapes.  In proceedings of IEEE ICRA 2011. retrieved from
        http://masc.cs.gmu.edu/wiki/uploads/GeneralizedMsum/
        icra11-dynsum-convex.pdf
        on 18 January 2012.

        arguments:
        other -- Polygon object
        r -- direction vector
        NOTE: GJK searches IN THE DIRECTION of r, thus r needs to point
        towards the origin with respect to the direction vector of self; in
        other words, if r represents the movement of self then client code
        should call raycast with -r.

        keyword arguments:
        s -- initial position along r, (0, 0) by default
        theta -- angular velocity in radians

        returns:
        if r does not intersect other, returns False
        else, returns the hit scalar, hit vector, and hit normal
        hit scalar -- the scalar where r intersects other
        hit vector -- the vector where self intersects other
        hit normal -- the edge normal at the intersection
        """
        self_rmax, other_rmax = self.rmax, other.rmax

        # max arc length of rotation
        # maximum radians for arc length is pi
        L = ((self_rmax * abs(_clamp(-pi, self_theta, pi))) +
             (other_rmax * abs(_clamp(-pi, other_theta, pi))))

        # polygons for support function; copied because they will be rotated
        A, B = Polygon(self), Polygon(other)
        support = _Support(A, B) # support mapping function s_P-Q(r)

        lambda_ = 0              # scalar of r to hit spot
        q = s                    # current point along r
        n = array([0, 0])        # hit normal at q

        v = support.get(r) - q   # vector from q to s_P-Q
        p = support.add(-v)      # support returns a v opposite of r
        w = p - q
        while dot(v, v) > _E * max(dot(p - q, p - q) for p in support):
            if dot(v, w) > 0:
                if (dot(v, r) <= 0) and (dot(v, v) >  (L * L)): return False
                n = -v
                # update lambda
                # translation distance lower bound := dot(v, w) / dot(v, r)
                # angular rotation distance lower bound := L * (1 - lambda)
                lambda_change = dot(v, w) / (dot(v, r) + (L * (1 - lambda_)))
                lambda_ = lambda_ + lambda_change
                if lambda_ > 1: return False
                # interpolate lambda
                q = s + (lambda_ * r) # translation
                A.rotate_ip(lambda_change * self_theta) # rotation
                B.rotate_ip(lambda_change * other_theta)
            v = support.v(q) # closest point to q in support points
            p = support.add(-v)
            w = p - q
        return lambda_, q, n


    def _A(self):
        # the area of polygon
        n = self.n
        P = self.P
        X, Y = P[:, 0], P[:, 1]
        return 0.5 * sum(X[i] * Y[(i + 1) % n] - X[(i + 1) % n] * Y[i]
                         for i in xrange(n))


    @property
    def C(self):
        """returns the centroid of the polygon"""
        a, n = self.a, self.n
        P = self.P
        X, Y = _unzip(P)

        if n == 1: return P[0]
        if n == 2: return array([X[0] + X[1] / 2, Y[0] + Y[1] / 2])

        c_x, c_y = 0, 0
        for i in xrange(n):
            a_i = X[i] * Y[(i + 1) % n] - X[(i + 1) % n] * Y[i]
            c_x += (X[i] + X[(i + 1) % n]) * a_i
            c_y += (Y[i] + Y[(i + 1) % n]) * a_i
        b = 1 / (6 * a)
        c_x *= b
        c_y *= b
        return array([c_x, c_y])


    @C.setter
    def C(self, x_y):
        x,y = x_y
        c_x, c_y = self.C
        x, y = x - c_x, y - c_y
        self.P = array([(p_x + x, p_y + y) for (p_x, p_y) in self.P])


    def _rotate(self, x0, theta, origin=None):
        if not origin: origin = self.C

        origin = origin.reshape(2, 1)
        x0 = x0.reshape(2, 1)
        x0 = x0 - origin # assingment operator (-=) would modify original x0

        A = array([[cos(theta), -sin(theta)], # rotation matrix
                   [sin(theta), cos(theta)]])

        return (dot(A, x0) + origin).ravel()


    def rotopoints(self, theta):
        """
        returns an array of points rotated theta radians around the centroid
        """
        P = self.P
        rotate = self._rotate
        return array([rotate(p, theta) for p in P])


    def rotoedges(self, theta):
        """return an array of vectors of edges rotated theta radians"""
        edges = self.edges
        rotate = self._rotate
        # edges, essentially angles, are always rotated around (0, 0)
        return array([rotate(edge, theta, origin=array([0, 0]))
                      for edge in edges])


    def rotate(self, theta): return Polygon(self.rotopoints(theta))


    def rotate_ip(self, theta):
        other = Polygon(self.rotopoints(theta))
        self.P[:] = other.P
        self.edges[:] = other.edges


    def project(self, axis):
        """project self onto axis"""
        P = self.P
        projected_points = [dot(p, axis) for p in P]
        # return the span of the projection
        return min(projected_points), max(projected_points)

    def intersection_points(self, other):
        """
        Determine contact (intersection) points between self
        and other.

        returns Empty list if no collisions found
        returns List of intersection points
        """
        points = []
        for i, p in enumerate(self.P):
            q = self.P[(i + 1) % len(self.P)]
            for j, r in enumerate(other.P):
                s = other.P[(j + 1) % len(other.P)]
                ipt = _line_intersect(p, q, r, s)
                if ipt: points.append(ipt)
        return points
