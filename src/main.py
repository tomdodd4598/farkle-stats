import itertools
import numba
import numpy as np

from fractions import Fraction


def range1(n):
    return range(1, 1 + n)


combo_data = []


def add_combo(nums, value):
    combo_data.append((np.array(nums), value))


def init_combos():
    add_combo([1, 2, 3, 4, 5, 6], 1500)
    add_combo([1], 100)
    add_combo([5], 50)

    for i in range1(6):
        if i > 1:
            add_combo([i] * 3, 100 * i)
        add_combo([i] * 4, 1000)
        add_combo([i] * 5, 2000)
        add_combo([i] * 6, 3000)

        for j in range1(6):
            if i != j:
                add_combo([i] * 3 + [j] * 3, 2500)

                for k in range1(6):
                    if i != k and j != k:
                        add_combo([i] * 2 + [j] * 2 + [k] * 2, 1500)


init_combos()


@numba.njit
def empty():
    return np.empty((0,), dtype=np.int32)


@numba.njit
def remove_elem(arr, elem):
    for i in range(arr.size):
        if elem == arr[i]:
            return True, np.delete(arr, i)
    return False, empty()


@numba.njit
def remove_all(arr, target):
    for elem in target:
        success, arr = remove_elem(arr, elem)
        if not success:
            return False, empty()
    return True, arr


def generate_scores(dice, scores, acc):
    for combo, points in combo_data:
        success, remaining = remove_all(dice, combo)
        if success:
            entry = scores.get(remaining.size)
            total = acc + points
            if not entry or entry < total:
                scores[remaining.size] = total
                generate_scores(remaining, scores, total)


def dice_perms(n):
    return itertools.combinations_with_replacement(range1(6), n)


def roll_score_data(n):
    data = []
    for roll in dice_perms(n):
        arr = np.array(roll)
        scores = {}
        generate_scores(arr, scores, 0)
        data.append((arr, scores))
    return data


@numba.njit
def perm_count(arr):
    res, i = 1, 1
    for a in np.bincount(arr):
        for j in range(1, 1 + a):
            res *= i
            res //= j
            i += 1
    return res


def main():
    for n in range1(6):
        data = roll_score_data(n)
        div = 6 ** n
        for arr, scores in data:
            prob = Fraction(perm_count(arr), div)
            print(arr, prob, scores)


if __name__ == '__main__':
    main()
