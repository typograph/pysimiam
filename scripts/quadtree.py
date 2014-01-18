from rect import Rect


class QuadTree(object):
    """ QuadTree data structure of simulated objects
    """
    
    #def __init__(self, xywh):
    #    self.rect = Rect(xywh)
        
    def __init__(self, items=None, depth=8, bounding_rect=None):
        """Creates a quad-tree.
 
        @param items:
            A sequence of items to store in the quad-tree.
            Note that these items must be of SimObject.
            
        @param depth:
            The maximum recursion depth.
            
        @param bounding_rect:
            The bounding rectangle of all of the items in the quad-tree.
            Type of Rect or (x,y,w,h) of the rectangle
            For internal use only.
        """
 
        # The sub-quadrants are empty to start with.
        self.nw = self.ne = self.se = self.sw = None
        self.depth = depth
        
        # Find this quadrant's centre.
        if bounding_rect:
            bounding_rect = Rect(bounding_rect)
        else:
            # If there isn't a bounding rect, then calculate it from the items.
            if items:
                bounding_rect = Rect(items[0].get_bounding_rect())
                for item in items[1:]:
                    bounding_rect.add(Rect(item.get_bounding_rect()))
            else:
                # in case there are no items, assume a big rect (100x100 meters)
                bounding_rect = Rect((0.0,0.0,100.0,100.0))
        
        self.rect = bounding_rect
        self.items = []
        
        # Insert items
        self.insert_items(items)
        #print("QuadTree:", self, self.items)
        
    def insert_items(self, items):
        """ Insert a list of SimObject items
        """
        # nothing to do if the list is empty or None
        if not items:
            return
        
        rect_items = [(item, Rect(item.get_bounding_rect()))
                      for item in items]
        
        # If we've reached the maximum depth then insert all items into
        # this quadrant.
        if self.depth <= 0 or not items:
            self.items += rect_items
            return
            
        cx, cy = self.rect.center
        nw_items = []
        ne_items = []
        se_items = []
        sw_items = []
        
        for item, item_rect in rect_items:
            # Which of the sub-quadrants does the item overlap?
            in_nw = item_rect.left <= cx and item_rect.top >= cy
            in_sw = item_rect.left <= cx and item_rect.bottom <= cy
            in_ne = item_rect.right >= cx and item_rect.top >= cy
            in_se = item_rect.right >= cx and item_rect.bottom <= cy
                
            # If it overlaps all 4 quadrants then insert it at the current
            # depth, otherwise append it to a list to be inserted under every
            # quadrant that it overlaps.
            if in_nw and in_ne and in_se and in_sw:
                self.items.append((item, item_rect))
            else:
                if in_nw: nw_items.append(item)
                if in_ne: ne_items.append(item)
                if in_se: se_items.append(item)
                if in_sw: sw_items.append(item)
            
        # Create the sub-quadrants, recursively.
        if nw_items:
            self.nw = QuadTree(nw_items, self.depth-1,
                               (self.rect.left, cy,
                                self.rect.width/2, self.rect.height/2))
        if ne_items:
            self.ne = QuadTree(ne_items, self.depth-1,
                               (cx, cy,
                                self.rect.width/2, self.rect.height/2))
        if se_items:
            self.se = QuadTree(se_items, self.depth-1,
                               (cx, self.rect.bottom,
                                self.rect.width/2, self.rect.height/2))
        if sw_items:
            self.sw = QuadTree(sw_items, self.depth-1, 
                               (self.rect.left, self.rect.bottom,
                                self.rect.width/2, self.rect.height/2))
    
    def find_items(self, xywh):
        """Returns the items that overlap a bounding rectangle.
 
        Returns the set of all items in the quad-tree that overlap with a
        bounding rectangle.
        
        @param xywh:
            The bounding rectangle being tested against the quad-tree.
        """
        rect = Rect(xywh)
        
        def overlaps(other):
            return rect.right >= other.left and rect.left <= other.right and \
                   rect.bottom <= other.top and rect.top >= other.bottom
        
        # Find the hits at the current level.
        hits = [item for item, item_rect in self.items
                if overlaps(item_rect)]
        
        # Recursively check the lower quadrants.
        cx, cy = self.rect.center
        if self.nw and rect.left <= cx and rect.top >= cy:
            hits += self.nw.find_items(rect)
        if self.sw and rect.left <= cx and rect.bottom <= cy:
            hits += self.sw.find_items(rect)
        if self.ne and rect.right >= cx and rect.top >= cy:
            hits += self.ne.find_items(rect)
        if self.se and rect.right >= cx and rect.bottom <= cy:
            hits += self.se.find_items(rect)
 
        return set(hits)
     
    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.rect)
