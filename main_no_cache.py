import itertools

from fractions import Fraction

# -------------------------------#
# ========== SETTINGS ========== #
# -------------------------------#

# Minimum score that can be banked.
min_total = 0  # default = 0

# Maximum score that should be banked.
target_total = 10000  # default = 10000

# Additional loss of points on farkling.
farkle_penalty = 0  # default = 0

# -------------------------------#
# ========== INTERNAL ========== #
# -------------------------------#

DICE = 6
SIDES = 6

combo_data = []
score_data = {}
cutoff_total = 0
roll_ev_cache = {}
best_score_cache = {}


def range1(n):
    return range(1, 1 + n)


def add_combo(nums, value):
    combo_data.append((nums, value))


def init_combos():
    add_combo([x for x in range1(SIDES)], 1500)
    add_combo([1], 100)
    add_combo([5], 50)

    for i in range1(SIDES):
        if i > 1:
            add_combo([i] * 3, 100 * i)
        add_combo([i] * 4, 1000)
        add_combo([i] * 5, 2000)
        add_combo([i] * 6, 3000)

        for j in range(1 + i, 1 + SIDES):
            add_combo([i] * 3 + [j] * 3, 2500)
            add_combo([i] * 2 + [j] * 4, 1500)
            add_combo([i] * 4 + [j] * 2, 1500)

            for k in range(1 + j, 1 + SIDES):
                add_combo([i] * 2 + [j] * 2 + [k] * 2, 1500)


def remove_elem(arr, elem):
    for i, x in enumerate(arr):
        if elem == x:
            return True, [y for j, y in enumerate(arr) if j != i]
    return False, []


def remove_all(arr, target):
    for elem in target:
        success, arr = remove_elem(arr, elem)
        if not success:
            return False, []
    return True, arr


def generate_scores(n, dice, scores, acc):
    for combo, points in combo_data:
        success, remaining = remove_all(dice, combo)
        if success:
            used = n - len(remaining)
            entry = scores.get(used)
            total = acc + points
            if not entry or entry < total:
                scores[used] = total
                generate_scores(n, remaining, scores, total)


def dice_perm_count(roll):
    res, i = 1, 1
    for a in range1(SIDES):
        for j in range1(roll.count(a)):
            res *= i
            res //= j
            i += 1
    return res


def dice_perms(n):
    return (list(x) for x in itertools.combinations_with_replacement(range1(SIDES), n))


def init_scores():
    for n in range1(DICE):
        div = SIDES ** n
        for roll in dice_perms(n):
            scores = {}
            generate_scores(n, roll, scores, 0)
            prob = Fraction(dice_perm_count(roll), div)
            score_data[tuple(roll)] = scores, prob


def total_ev(t, n):
    if t >= cutoff_total:
        return t
    elif t >= min_total:
        return t + max(0, roll_ev_cache[t][n - 1])
    else:
        return t + roll_ev_cache[t][n - 1]


def next_n(n):
    return DICE if n == 0 else n


def best_score_info(t, roll):
    best_u, best_s, best_tev = 0, 0, 0
    dice = len(roll)

    roll_tuple = tuple(roll)
    scores, prob = score_data[roll_tuple]
    for u, s in scores.items():
        if s != 0:
            tev = total_ev(t + s, next_n(dice - u))
            if best_s == 0 or tev > best_tev:
                best_u, best_s, best_tev = u, s, tev

    result = best_u, best_s, prob
    if cutoff_total > 0:
        best_score_cache[(t, roll_tuple)] = result
    return result


def calc_roll_ev(t, n):
    result = 0
    for roll in dice_perms(n):
        u, s, prob = best_score_info(t, roll)
        if s == 0:
            result -= (t + farkle_penalty) * prob
        else:
            result += (total_ev(t + s, next_n(n - u)) - t) * prob
    return result


def is_valid_cutoff_total(t):
    return calc_roll_ev(t, DICE) < 0


def init_cutoff():
    low = 0
    high = 50

    while not is_valid_cutoff_total(high):
        low = high
        high *= 2
        if high >= target_total - 50:
            high = target_total - 50
            break

    while high - low > 50:
        mid = 50 * ((high + low) // 100)
        if is_valid_cutoff_total(mid):
            high = mid
        else:
            low = mid

    global cutoff_total
    cutoff_total = max(high, min_total)


def init_roll_evs():
    for t in range(cutoff_total, -50, -50):
        data = []
        roll_ev_cache[t] = data
        for n in range1(DICE):
            data.append(calc_roll_ev(t, n))


def main():
    print('Compiling dice combos...')
    init_combos()

    print('Compiling roll scores...')
    init_scores()

    print('Calculating cutoff total...')
    init_cutoff()

    print('Calculating roll EVs...')
    init_roll_evs()

    print()

    def query_help():
        print('h                   : Display help.')
        print('r [total] [dice]    : Expected value of roll with the current total and available dice.')
        print('                      Example: \'r 200 4\'')
        print('s [total] [roll...] : Best choice of dice to score with the current total and rolled dice.')
        print('                      Example: \'s 400 1 5 5\'')
        print('q                   : Quit program.')

    while True:
        inp = input('Enter query: ').split()
        c = len(inp)
        if c > 0:
            fst = inp[0].lower()
            if c == 1 and fst == 'q':
                break
            elif c == 1 and fst == 'h':
                query_help()
                continue
            elif c == 3 and fst == 'r' and inp[1].isnumeric() and inp[2].isnumeric():
                roll_ev, dice = roll_ev_cache.get(int(inp[1])), int(inp[2])
                if roll_ev and 1 <= dice <= DICE:
                    ev = roll_ev[dice - 1]
                    action = 'ROLL!' if ev > 0 else 'BANK!'
                    print(f'EV = {float(ev)} -> {action}')
                else:
                    print('Roll data does not exist for this input!')
                continue
            elif 2 < c <= 2 + DICE and fst == 's' and all(x.isnumeric() for x in inp[1:]):
                t = int(inp[1])
                best_score = best_score_cache.get((t, tuple(sorted(int(x) for x in inp[2:]))))
                if best_score:
                    u, s, _ = best_score
                    if s == 0:
                        if t == 0:
                            print(f'You immediately farkled!')
                            if farkle_penalty > 0:
                                print(f'Lose {farkle_penalty} banked points as a penalty.')
                        else:
                            print(f'You farkled!')
                            print(f'Lose all {t} accumulated points', end='' if farkle_penalty > 0 else '.\n')
                            if farkle_penalty > 0:
                                print(f', as well as {farkle_penalty} banked points as a penalty.')

                    else:
                        def d(x):
                            return 'die' if x == 1 else 'dice'

                        r = c - u - 2
                        print(f'Score {s} with {u} {d(u)}.')
                        print(f'You now have a current total of {t + s} and {r} available {d(r)}.')
                else:
                    print('Score data does not exist for this input!')
                continue

        print('Could not parse input! Enter \'h\' for help.')


if __name__ == '__main__':
    main()
