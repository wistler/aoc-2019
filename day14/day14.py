import sys, os, math

ORE = 'ORE'
FUEL = 'FUEL'


def parse_seg(seg):
    count, label = seg.strip().split()
    return label, int(count)


def parse_line(line):
    l, r = list(map(str.strip, line.split(' => ')))
    ri = parse_seg(r)
    lin = [parse_seg(li) for li in l.split(', ')]
    return ri, lin


def make(target, formula_dict, needs=None, stock=None, debug=False):
    if debug:
        print('make({target}): stock: {stock}'.format(**locals()))

    needs = needs or {}
    stock = stock or {}

    tn, tc = target  # (name, count)

    if tn in stock:
        if debug:
            print('make({target}): already in stock: {stock_tn}'.format(**locals(), stock_tn=stock[tn]))
        # Don't remove from stock, just check if there's enough there!
        stock[tn], tc = max(0, stock[tn] - tc), max(0, tc - stock[tn])

    if tc == 0:
        if debug:
            print('make({target}): ALL IN STOCK: {stock_tn}'.format(**locals(), stock_tn=stock[tn]))
        # There was already stuff in stock, no new materials needed.
        return needs, stock

    for key, value in formula_dict.items():
        kn, kc = key  # (name, count)
        if tn == kn:  # found the formula
            mult = math.ceil( tc / kc )  # no less than 1x
            if debug:
                print('make({target}): Needs BEFORE update: {needs}'.format(**locals()))
                print('make({target}): Stock BEFORE update: {stock}'.format(**locals()))
            needs = {**needs, **dict((vn, vc*mult + (needs[vn] if vn in needs else 0) ) for vn, vc in value)}
            stock = {**stock, **{tn: kc*mult + (stock[tn] if tn in stock else 0) - tc}}
            if stock[tn] == 0:
                del stock[tn]
            if debug:
                print('make({target}): Needs AFTER update: {needs}'.format(**locals()))
                print('make({target}): Stock AFTER update: {stock}'.format(**locals()))
            
            return needs, stock
    
    raise Exception("Lookup Error: Cannot fint target in formula: {}".format(target))


def make_from_ore(target, formula_dict, needs=None, stock=None, debug=False):
    """ recursively make all needs until ORE becomes the only need """
    if debug:
        print('make_from_ore({target}): needs:{needs}, stock: {stock}'.format(**locals()))

    needs = needs or {}
    stock = stock or {}

    if debug:
        print('make_from_ore({target}): Needs BEFORE update: {needs}'.format(**locals()))
        print('make_from_ore({target}): Stock BEFORE update: {stock}'.format(**locals()))

    needs, stock = make(target, formula_dict, needs, stock, debug=debug)

    if debug:
        print('make_from_ore({target}): Needs AFTER update: {needs}'.format(**locals()))
        print('make_from_ore({target}): Stock AFTER update: {stock}'.format(**locals()))

    if len(needs) > 0:
        l = list(needs.keys())

        if ORE in l:
            l.remove(ORE)

        if len(l) > 0:

            tn = l.pop()
            target = tn, needs.pop(tn)
            needs, stock = make_from_ore(target, formula_dict, needs, stock, debug=debug)

    # if debug:
    #     print('make_from_ore({target}): DONE!! Returning: needs:{needs}, stock: {stock}'.format(**locals()))

    return needs, stock


def make_until_depleted(target, formula_dict, limit=1_000_000_000_000, needs=None, stock=None, debug=False):
    needs = needs or {ORE: 0}
    stock = stock or {}

    fuel = 0
    while needs[ORE] < limit:        
        _needs, _stock = make_from_ore(target, formula_dict, needs=needs, stock=stock, debug=False)

        if debug:
            print(needs, stock, _needs, _stock)

        if _needs[ORE] >= limit:
            break

        fuel += target[1]
        needs, stock = _needs, _stock

    if target[1] > 1:
        new_target = int(target[1] / 2)
        fuel += make_until_depleted((target[0], new_target), formula_dict, limit=limit, needs=needs, stock=stock, debug=debug)

    if debug:
        print("Made fuel: {} from ore: {}".format(fuel, needs[ORE]))
    
    return fuel


def run_tests():
    text = """
    10 ORE => 10 A
    1 ORE => 1 B
    7 A, 1 B => 1 C
    7 A, 1 C => 1 D
    7 A, 1 D => 1 E
    7 A, 1 E => 1 FUEL
    """
    formulae = dict( parse_line(line) for line in text.splitlines() if len(line.strip()) != 0 )
    print(formulae)
    print(make((FUEL, 1), formulae))
    print(make(('A', 1), formulae))
    print('---')
    print(make_from_ore(('A', 1), formulae))
    print('RESULT:', make_from_ore((FUEL, 1), formulae))

    text = """
    9 ORE => 2 A
    8 ORE => 3 B
    7 ORE => 5 C
    3 A, 4 B => 1 AB
    5 B, 7 C => 1 BC
    4 C, 1 A => 1 CA
    2 AB, 3 BC, 4 CA => 1 FUEL
    """.strip()
    formulae = dict( parse_line(line) for line in text.splitlines() if len(line.strip()) != 0 )
    print('RESULT:', make_from_ore((FUEL, 1), formulae))
    print('MAX FUEL:', make_until_depleted((FUEL, 1_000_000_000), formulae, limit=1_000_000_000_000, debug=False))

    text = """
    157 ORE => 5 NZVS
    165 ORE => 6 DCFZ
    44 XJWVT, 5 KHKGT, 1 QDVJ, 29 NZVS, 9 GPVTF, 48 HKGWZ => 1 FUEL
    12 HKGWZ, 1 GPVTF, 8 PSHF => 9 QDVJ
    179 ORE => 7 PSHF
    177 ORE => 5 HKGWZ
    7 DCFZ, 7 PSHF => 2 XJWVT
    165 ORE => 2 GPVTF
    3 DCFZ, 7 NZVS, 5 HKGWZ, 10 PSHF => 8 KHKGT
    """.strip()
    formulae = dict( parse_line(line) for line in text.splitlines() if len(line.strip()) != 0 )
    print('RESULT:', make_from_ore((FUEL, 1), formulae))
    print('MAX FUEL:', make_until_depleted((FUEL, 1_000_000_000), formulae))


    text = """
2 VPVL, 7 FWMGM, 2 CXFTF, 11 MNCFX => 1 STKFG
17 NVRVD, 3 JNWZP => 8 VPVL
53 STKFG, 6 MNCFX, 46 VJHF, 81 HVMC, 68 CXFTF, 25 GNMV => 1 FUEL
22 VJHF, 37 MNCFX => 5 FWMGM
139 ORE => 4 NVRVD
144 ORE => 7 JNWZP
5 MNCFX, 7 RFSQX, 2 FWMGM, 2 VPVL, 19 CXFTF => 3 HVMC
5 VJHF, 7 MNCFX, 9 VPVL, 37 CXFTF => 6 GNMV
145 ORE => 6 MNCFX
1 NVRVD => 8 CXFTF
1 VJHF, 6 MNCFX => 4 RFSQX
176 ORE => 6 VJHF
    """.strip()
    formulae = dict( parse_line(line) for line in text.splitlines() if len(line.strip()) != 0 )
    print('RESULT:', make_from_ore((FUEL, 1), formulae))
    print('MAX FUEL:', make_until_depleted((FUEL, 1_000_000_000), formulae))

    text = """
171 ORE => 8 CNZTR
7 ZLQW, 3 BMBT, 9 XCVML, 26 XMNCP, 1 WPTQ, 2 MZWV, 1 RJRHP => 4 PLWSL
114 ORE => 4 BHXH
14 VRPVC => 6 BMBT
6 BHXH, 18 KTJDG, 12 WPTQ, 7 PLWSL, 31 FHTLT, 37 ZDVW => 1 FUEL
6 WPTQ, 2 BMBT, 8 ZLQW, 18 KTJDG, 1 XMNCP, 6 MZWV, 1 RJRHP => 6 FHTLT
15 XDBXC, 2 LTCX, 1 VRPVC => 6 ZLQW
13 WPTQ, 10 LTCX, 3 RJRHP, 14 XMNCP, 2 MZWV, 1 ZLQW => 1 ZDVW
5 BMBT => 4 WPTQ
189 ORE => 9 KTJDG
1 MZWV, 17 XDBXC, 3 XCVML => 2 XMNCP
12 VRPVC, 27 CNZTR => 2 XDBXC
15 KTJDG, 12 BHXH => 5 XCVML
3 BHXH, 2 VRPVC => 7 MZWV
121 ORE => 7 VRPVC
7 XCVML => 6 RJRHP
5 BHXH, 4 VRPVC => 5 LTCX
    """.strip()
    formulae = dict( parse_line(line) for line in text.splitlines() if len(line.strip()) != 0 )
    print('RESULT:', make_from_ore((FUEL, 1), formulae))
    print('MAX FUEL:', make_until_depleted((FUEL, 1_000_000_000), formulae))



if __name__ == '__main__':
    run_tests()

    print("Reading input..")
    with open('./day14/input') as input:
        text = input.readlines()
    formulae = dict( parse_line(line) for line in text if len(line.strip()) != 0 )
    print('RESULT:', make_from_ore((FUEL, 1), formulae))
    print('MAX FUEL:', make_until_depleted((FUEL, 1_000_000_000), formulae))
    