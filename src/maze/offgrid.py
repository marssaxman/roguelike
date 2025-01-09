#!/usr/bin/env python
# Port of Chris Cox's offgrid algorithm, originally found here:
#  https://gitlab.com/chriscox/offgrid.git

# method of use: call `generate`, iterate over resulting rectangles

import numpy as np

def hash64(x: np.int64) -> np.int64:
    ux = np.uint64(x)
    a = np.uint64(6364136223846793005)
    c = np.uint64(1442695040888963407)
    # we must call the numpy functions explicitly or we will get a warning
    # about overflow, which is intentionally part of the algorithm here
    temp: np.uint64 = np.add(np.multiply(ux, a), c, dtype=np.uint64)
    righter: np.uint64 = np.right_shift(temp, 20, dtype=np.uint64)
    lefter: np.uint64 = np.left_shift(temp, 23, dtype=np.uint64)
    return np.int64(righter ^ lefter ^ temp)


def hashXY(x: np.int64, y: np.int64, seed: np.int64) -> np.int64:
    return hash64( hash64(x) ^ (y^seed) );


def hash_to_double(x: np.int64) -> np.double:
    BITS = np.uint64(30)
    MASK: np.uint = np.left_shift(1, BITS, dtype=np.uint64) - np.uint(1)
    scale: np.double = 1.0 / np.double(MASK);

    result = np.bitwise_and(np.uint64(x), MASK, dtype=np.uint64) * scale;
    return result


def hashXY_float(x: np.int64, y: np.int64, seed: np.int64) -> np.double:
    temp = hashXY(x, y, seed);
    result = hash_to_double(temp)
    return result


def box_random(
    x: np.int64,
    y: np.int64,
    seed: np.int64,
    edge: np.double # range 0..0.5
) -> np.double:
    range = 1.0 - 2.0 * edge
    random = hashXY_float(x, y, seed)
    result = edge + range * random
    return result


class rectFloat:
    def __init__(self, t: np.double, l: np.double, b: np.double, r: np.double):
        self.top = t
        self.left = l
        self.bottom = b
        self.right = r

    # also fails for NaNs
    def isValid(self):
        return (self.top < self.bottom) and (self.left < self.right)


def CellToRect(
    ix: np.int64,
    iy: np.int64,
    seed: np.int64,
    edge: np.double # range: 0..0.5
) -> rectFloat:
    # checkerboard even and odd, vertical and horizontal limits
    even = np.bitwise_and(np.bitwise_xor(ix, iy), 0x01) == 0

    fx = np.double(ix)
    fy = np.double(iy)

    horiz_limit: np.double
    vert_limit: np.double
    vert2_limit: np.double
    horiz2_limit: np.double

    if even:
        horiz_limit = fx + box_random(ix, iy, seed, edge)
        vert_limit = fy + box_random(ix+1, iy, seed, edge)
        vert2_limit = fy + box_random(ix, iy+1, seed, edge) + 1.0
        horiz2_limit = fx + box_random(ix+1, iy+1, seed, edge) + 1.0
    else:
        vert_limit = fy + box_random(ix, iy, seed, edge)
        horiz_limit = fx + box_random(ix, iy+1, seed, edge)
        horiz2_limit = fx + box_random(ix+1, iy, seed, edge) + 1.0
        vert2_limit = fy + box_random(ix+1, iy+1, seed, edge) + 1.0

    # here, the limits are always in known order
    left = np.double(horiz_limit)
    right = np.double(horiz2_limit)
    top = np.double(vert_limit)
    bottom = np.double(vert2_limit)
    assert(left <= right)
    assert(top <= bottom)

    return rectFloat(top, left, bottom, right)


def generate(
    width: np.uint,
    height: np.uint,
    box_size: np.uint,
    seed: np.int64,
    edge: np.double = np.double(0.1) # range: 0..0.5
):
    boxes_wide = np.floor_divide(width, box_size, dtype=np.int64)
    boxes_high = np.floor_divide(height, box_size, dtype=np.int64)

    # We have to overscan the grid slightly because displaced rects will
    # overlap edges. ...and the scaled, centered coordinate system complicates
    # things a little bit.
    for y in np.arange(-2, boxes_high+1, dtype=np.int64):
        for x in np.arange(-2, boxes_wide+1, dtype=np.int64):
            half_wide = np.floor_divide(boxes_wide, 2)
            half_high = np.floor_divide(boxes_high, 2)
            theRect = CellToRect(x - half_wide, y - half_high, seed, edge)

            # edge values will always match up between rects, because of the
            # way they are calculated uniquely per edge
            # we just need to round consistently for them to draw correctly
            top: np.int64
            left: np.int64
            bottom: np.int64
            right: np.int64
            box_top = np.int64(np.floor(box_size * theRect.top))
            box_left = np.int64(np.floor(box_size * theRect.left))
            box_bottom = np.int64(np.floor(box_size * theRect.bottom))
            box_right = np.int64(np.floor(box_size * theRect.right))
            top = np.int64(box_top + height/2 + 1)
            left = np.int64(box_left + width/2 + 1)
            bottom = np.int64(box_bottom + height/2 + 1)
            right = np.int64(box_right + width/2 + 1)

            yield (left, top, right, bottom)


def OffGridPrintf(
    width: np.uint,
    height: np.uint,
    box_size: np.uint,
    seed: np.int64,
    edge: np.double = np.double(0.1) # range: 0..0.5
):
    boxes_wide = np.floor_divide(width, box_size, dtype=np.int64)
    boxes_high = np.floor_divide(height, box_size, dtype=np.int64)
    print(f"boxes_wide={boxes_wide}, boxes_high={boxes_high}")

    # We have to overscan the grid slightly because displaced rects will
    # overlap edges. ...and the scaled, centered coordinate system complicates
    # things a little bit.
    for y in np.arange(-2, boxes_high+1, dtype=np.int64):
        for x in np.arange(-2, boxes_wide+1, dtype=np.int64):
            half_wide = np.floor_divide(boxes_wide, 2)
            half_high = np.floor_divide(boxes_high, 2)
            theRect = CellToRect(x - half_wide, y - half_high, seed, edge)

            # edge values will always match up between rects, because of the
            # way they are calculated uniquely per edge
            # we just need to round consistently for them to draw correctly
            box_top = np.int64( np.floor(box_size*theRect.top) )
            top = np.int64(box_top + height/2 + 1)
            box_left = np.int64( np.floor(box_size*theRect.left) )
            left = np.int64(box_left + width/2 + 1)
            box_bottom = np.int64( np.floor(box_size*theRect.bottom) )
            bottom = np.int64(box_bottom + height/2 + 1)
            box_right = np.int64( np.floor(box_size*theRect.right) )
            right = np.int64(box_right + width/2 + 1)

            print(f"(x:{x}, y:{y}) = {{l:{left}, t:{top}, r:{right}, b:{bottom}}}")


if __name__ == "__main__":
    shared_seed: np.int64 = hash64(np.int64(0x8675309))

    print(f"shared_seed: {shared_seed}")
    width = np.uint(80)
    height = np.uint(50)
    box_size = np.uint(15)
    OffGridPrintf(width, height, box_size, shared_seed)

