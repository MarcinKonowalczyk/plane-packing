from plane_packing import Plane
from random import shuffle

def pack_plane(rows, seats):
    p = Plane(rows,seats)

    destinations = p.all_destinations()
    shuffle(destinations)

    # images = []
    # SIZE = 4

    j=0  # Iteration count

    # images.append(p.to_image(SIZE))
    p.spawn(destinations[0],1)
    del destinations[0]
    j+=1
    # images.append(p.to_image(SIZE))

    while not p.happy:
        if len(destinations) > 0:
            dest = destinations[0]
            success = p.spawn(dest)
            if success:
                del destinations[0]
        
        p.update_passengers()
        j += 1
        # images.append(p.to_image(SIZE))
    return j