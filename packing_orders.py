from plane_packing import Plane, pack_plane
from random import shuffle, sample

def random_order(rows, seats):
    ''' Allow the passengers into the plane in a random order '''
    p = Plane(rows,seats)

    dest = p.all_destinations()
    shuffle(dest)

    n = pack_plane(p, dest)
    return n

def back_to_front(rows, seats):
    ''' Back to front with random seat allocations '''
    p = Plane(rows,seats)

    dest = []
    for row in reversed(p._grid):
        dest += sample([(e.row, e.seat) for e in row if e.seat != 0],2*p.seats)
    
    n = pack_plane(p,dest)
    return n

def front_to_back(rows, seats):
    ''' Front to back with random seat allocations '''
    p = Plane(rows,seats)

    dest = []
    for row in p._grid:
        dest += sample([(e.row, e.seat) for e in row if e.seat != 0],2*p.seats)
    
    n = pack_plane(p,dest)
    return n

def windows_first(rows, seats):
    ''' Random rows, but window seats first '''
    p = Plane(rows,seats)
    
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
    
    n = pack_plane(p,dest)
    return n

def alley_first(rows, seats):
    ''' Random rows, but alley seats first '''
    p = Plane(rows,seats)
    
    grid = {}
    for j in range(p.seats):
        grid[j+1] = []
    for col in zip(*p._grid):
        if col[0].seat != 0:
            grid[abs(col[0].seat)] += [(e.row, e.seat) for e in col]
    dest = []
    for j in range(p.seats):
        dest += sample(grid[j+1],len(grid[j+1]))
    
    n = pack_plane(p,dest)
    return n