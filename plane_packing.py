from warnings import warn
import numpy as np
from PIL import Image
from random import shuffle, randint

class Cell:

    @property
    def links(self):
        return list(self._links.keys())

    @property
    def n_of_links(self, row, seat):
        ''' Number of links '''
        return len(self.links)

    def __init__(self, row, seat):
        self.row = row
        self.seat = seat

        self.up = None
        self.down = None
        self.left = None
        self.right = None

        self._links = {}
        self._data = {}
        self.passenger = None

    def link(self, cell, bidi = True):
        ''' Link yourself to another cell '''
        if is_cell(cell):
            self._links[cell] = True
            if bidi: cell.link(self, False)
        else:
            raise ValueError('Link can be made/broken only between two cells')

    def __iadd__(self, cell):
        ''' Overload for the += operator with the link method '''
        self.link(cell)
        return self

    def unlink(self, cell, bidi = True):
        ''' Unlink yourself from another cell '''
        if is_cell(cell):
            if cell in self.links:
                del self._links[cell]
                if bidi: cell.unlink(self, False)
        elif cell is None:
            warn('Attempted link to None. No link has been made.')
        else:
            raise ValueError('Link can be made/broken only between two cells')

    def __isub__(self, cell):
        ''' Overload for the -= operator with the unlink method '''
        self.unlink(cell)
        return self

    def linked(self, cell):
        ''' Check if this cell is linked to another '''
        if is_cell(cell):
            return cell in self.links
        elif cell is None:
            return False
        else:
            raise ValueError('Cells can be linked only to other cells')

    def __and__(self, other):
        ''' Overload for the & operator with the linked? method '''
        return self.linked(other)

    @property
    def data(self):
        ''' Accesses the data dictionary '''
        return self._data

    @property
    def has_data(self, key):
        ''' Checks wheter cell contains key '''
        return key in self.data.keys()

    @property
    def has_passenger(self):
        ''' Check whether there is someone in this cell '''
        return self.passenger is not None

    @property
    def is_alley(self):
        ''' Check wheter cell is an alley cell '''
        return self.seat == 0

    @property
    def is_seat(self):
        ''' Check wheter cell is a seat cell '''
        return not self.is_alley

    def __hash__(self) -> int:
        ''' Unique hash of the cell '''
        return id(self)

    def __repr__(self) -> str:
        ''' Representation of cell for print()/format() calls '''
        row = self.row
        seat = self.seat
        if self.seat == 0:
            return 'Alley cell in row {}'.format(row)
        else:
            return 'Seat cell in row {}, seat {}'.format(row,seat)

    def __eq__(self, other):
        ''' Overload the == operator '''
        if is_cell(other):
            return hash(self) == hash(other)
        else:
            return False

    def __ne__(self, other):
        ''' Overload the != operator '''
        return not self == other

def is_cell(cell):
    ''' Check wheter is a cell '''
    return isinstance(cell, Cell)

class Plane:
    ''' Simple plane setup '''
    def __init__(self, rows, seats):
        if rows is None or rows < 2:
            raise ValueError('Rows must be an integer greater than 1')
        if seats is None or seats < 2:
            raise ValueError('Seats must an integer greater than 1')

        self.rows = rows
        self.seats = seats
        self._grid = self.create_grid(rows, seats)
        self._passengers = []
        self.configure_cells()

    @staticmethod
    def create_grid(rows, seats):
        ''' Create the grid '''
        return [[Cell(row,seat) for seat in range(-seats,seats+1)] for row in range(rows)]

    def configure_cells(self):
        ''' Create all the dependencies of the cells '''
        for cell in self.each_cell():
            row = cell.row
            seat = cell.seat

            cell.up = self[row - 1, seat]
            cell.down = self[row + 1, seat]
            cell.left = self[row, seat - 1]
            cell.right = self[row, seat + 1]

    @property
    def n_of_seats(self):
        ''' Number of seats on the plane'''
        return 2*self.rows*self.seats
    
    @property
    def n_of_passengers(self):
        ''' Number of passengers on the plane '''
        return len(self._passengers)

    @property
    def entrace_cell(self):
        return self[0, 0]

    def each_row(self):
        ''' Access each row '''
        for row in self._grid:
            yield row
    
    def each_cell(self):
        ''' Access each cell '''
        for row in self.each_row():
            for cell in row:
                yield cell

    def each_alley_cell(self):
        ''' Return all the alley cells '''
        for row in self._grid:
            yield row[self.seats]
    
    def all_destinations(self):
        ''' All destinations of self '''
        destinations = []
        for cell in self.each_cell():
            if cell.is_seat:
                destinations.append((cell.row, cell.seat))
        return destinations

    def __getitem__(self, key):
        ''' Get grid item method '''
        if type(key) == tuple and len(key) == 2:
            row, seat = key
            if row < 0 or row > self.rows - 1: return None
            if seat < -self.seats or seat > self.seats: return None
            return self._grid[row][seat+self.seats]
        else:
            raise IndexError('Only grid[row,col] __getitem__ calls are supported')

    def spawn(self, destination, actions=0, sprite=None):
        ''' Spawn new passenger with a specified destination '''
        ec = self.entrace_cell
        if ec.has_passenger:
            return False
        p = Passenger(0, 0, ec, destination, actions=actions, sprite=sprite)
        ec.passenger = p
        self._passengers.append(p)
        return True
    
    @property
    def passengers(self):
        ''' All the passengers '''
        for passenger in self._passengers:
            yield passenger

    def update_passengers(self):
        ''' Update all the passengers '''
        for passenger in self.passengers:
            passenger.update()
        for passenger in self.passengers:
            passenger.actions = 1

    @property
    def passengers_in_place(self):
        ''' Check whether all the passengers are in place '''
        for passenger in self.passengers:
            if not passenger.is_in_place:
                return False
        return True

    @property
    def all_passengers_present(self):
        ''' Check wheter all the passengers are present '''
        return self.n_of_passengers == self.n_of_seats

    @property
    def happy(self):
        ''' Cehck that all the passengers are in place and present '''
        return self.all_passengers_present and self.passengers_in_place

    def to_image(self, size=1):
        ''' Create image representation of the plane '''
        alley_sprite = Image.open('sprites/alley_{}x.png'.format(size))
        seat_sprite = Image.open('sprites/seat_{}x.png'.format(size))
        cs = 16*size

        image_rows = (self.rows)*cs
        image_cols = (2*self.seats+1)*cs
        arr = np.zeros((image_rows, image_cols, 3))  # RGB image
        for cell in self.each_cell():
            row = cell.row
            seat = cell.seat
            col = seat + self.seats
            
            if seat == 0:
                cell_sprite = alley_sprite.copy()
            else:
                cell_sprite = seat_sprite.copy()
            
            if cell.has_passenger:
                passenger_sprite = Image.open('sprites/passenger{}_{}x.png'.format(cell.passenger.sprite, size))
                cell_sprite.paste(passenger_sprite, (0, 0), passenger_sprite)
                if cell.passenger.is_paused:
                    pause_sprite = Image.open('sprites/pause_{}x.png'.format(size))
                    cell_sprite.paste(pause_sprite, (0, 0), pause_sprite)
            cell_sprite = cell_sprite.convert('RGB')  # Remove alpha channel

            arr[row*cs:(row+1)*cs, col*cs:(col+1)*cs, 0:3] = np.array(cell_sprite)

        return Image.fromarray(np.uint8(arr))

class Passenger:
    def __init__(self, row, seat, parent, destination, actions=0, sprite=None):
        self.parent_cell = parent
        self.actions = actions
        self.pause = 0
        self.row = row
        self.seat = seat
        self.destination = destination
        self.sprite = sprite if sprite is not None else randint(1,6)

    @property
    def has_actions(self):
        ''' Check whether has actions left '''
        return self.actions > 0

    @property
    def is_paused(self):
        ''' Check whether is paused '''
        return self.pause > 0
    
    @property
    def is_in_place(self):
        ''' Check wheter passenger is in place '''
        return self.row == self.destination[0] and self.seat == self.destination[1]

    def update(self):
        ''' Update the state of self according to destination '''
        if self.pause > 0:
            self.pause -= 1
            return

        drow = self.destination[0]  # Destination row
        dseat = self.destination[1]  # Destination seat

        if self.row < drow:
            self.move_down()
        elif self.row > drow:
            self.move_up()
        else:
            if self.seat < dseat:  # Going right
                if self.parent_cell.right.has_passenger:
                    self._shuffle(self.parent_cell.right.passenger)
                else:
                    self.move_right()
            elif self.seat > dseat:  # Going left
                if self.parent_cell.left.has_passenger:
                    self._shuffle(self.parent_cell.left.passenger)
                else:
                    self.move_left()
            else:
                pass
    
    def move_down(self):
        ''' Attempt to move down '''
        if self.seat is not 0:
            return
        self._move(self.parent_cell.down)
    
    def move_up(self):
        ''' Attempt to move up '''
        if self.seat is not 0:
            return
        self._move(self.parent_cell.up)

    def move_left(self):
        ''' Attempt to move left '''
        self._move(self.parent_cell.left)

    def move_right(self):
        ''' Attempt to move right '''
        self._move(self.parent_cell.right)

    def _shuffle(self, other):
        ''' Shuffle sround with another passenger '''
        if not self.has_actions or not other.has_actions or other.is_paused:
            pass
        self.actions -= 1
        other.actions -= 1

        parent = self.parent_cell
        destination = other.parent_cell

        parent.passenger = other
        destination.passenger = self
        other.parent_cell = parent
        self.parent_cell = destination

        # Update the position of self
        self.row = destination.row
        self.seat = destination.seat

        # Update the position of other
        other.row = parent.row
        other.seat = parent.seat

        other.pause = 1  # Pause the other

    def _move(self, destination):
        ''' Attempt to move to the destination '''
        if not self.has_actions:
            return
        self.actions -= 1

        parent = self.parent_cell

        if destination.has_passenger:
            return  # Can't occupy the same cell
        else:
            # Break and make the links
            parent.passenger = None
            destination.passenger = self
            self.parent_cell = destination

            # Update the position of self
            self.row = destination.row
            self.seat = destination.seat


def pack_plane(plane, destinations):
    ''' Pack the plane for given plane and list of destinantions '''
    p = plane
    n = 0  # Iteration count
    p.spawn(destinations[0],1)
    del destinations[0]
    n += 1

    while not p.happy:
        if len(destinations) > 0:
            dest = destinations[0]
            success = p.spawn(dest)
            if success:
                del destinations[0]
        p.update_passengers()
        n += 1
    return n

def pack_plane_animate(plane, destinations, filename, size=4):
    ''' Simple animation of plane packing '''
    p = plane
    images = []
    n = 0  # Iteration count
    images.append(p.to_image(size))
    p.spawn(destinations[0],1)
    del destinations[0]
    n += 1
    images.append(p.to_image(size))

    while not p.happy:
        if len(destinations) > 0:
            dest = destinations[0]
            success = p.spawn(dest)
            if success:
                del destinations[0]
        
        p.update_passengers()
        n += 1
        images.append(p.to_image(size))
    
    images[0].save('{}.gif'.format(filename),
               save_all=True,
               append_images=images[1:],
               duration=len(images),
               loop=0) 