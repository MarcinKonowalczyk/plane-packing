from plane_packing import Plane
from random import sample

def random_order(plane):
    ''' Allow the passengers into the plane in a random order '''
    p = plane
    dest = p.all_destinations()
    dest = sample(dest,len(dest))
    return dest

def back_to_front(plane):
    ''' Back to front with random seat allocations '''
    p = plane
    dest = []
    for row in reversed(p._grid):
        dest += sample([(e.row, e.seat) for e in row if e.seat != 0],2*p.seats)
    return dest

def front_to_back(plane):
    ''' Front to back with random seat allocations '''
    p = plane
    dest = []
    for row in p._grid:
        dest += sample([(e.row, e.seat) for e in row if e.seat != 0],2*p.seats)
    return dest

def windows_first(plane):
    ''' Random rows, but window seats first '''
    p = plane
    
    # This was surprisingly difficult!!
    grid = {}
    for j in range(p.seats):
        grid[j+1] = []
    for col in zip(*p._grid):
        if col[0].seat != 0:
            grid[abs(col[0].seat)] += [(e.row, e.seat) for e in col]
    dest = []
    for j in reversed([i for i in range(p.seats)]):
        dest += sample(grid[j+1], len(grid[j+1]))
    
    return dest

def alley_first(plane):
    ''' Random rows, but alley seats first '''
    p = plane

    grid = {}
    for j in range(p.seats):
        grid[j+1] = []
    for col in zip(*p._grid):
        if col[0].seat != 0:
            grid[abs(col[0].seat)] += [(e.row, e.seat) for e in col]
    dest = []
    for j in range(p.seats):
        dest += sample(grid[j+1],len(grid[j+1]))
    
    return dest