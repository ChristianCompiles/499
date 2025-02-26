#import random
#import hashlib
#import time
from functools import reduce

from secrets import randbelow
#import gmpy2
from gmpy2 import mpz, is_prime, mpz_random
#import math
from math import isqrt
#from typing import Optional
from random import randrange
from sympy import isprime, nextprime, primitive_root, randprime

def discrete_log_bound(a, g, bounds):
    """
    Find the discrete log of a under base g within bounds using Pollard's Kangaroo algorithm

    :param a: Target element
    :param g: Base element
    :param bounds: Bounds for discrete log search
    :return: Discrete log of a under base g
    """
    width = bounds[1] - bounds[0]
    if width < 1000:
        return discrete_log_bound_brute(a, g, bounds)

    lb = bounds[0]
    ub = bounds[1]

    N = isqrt(width) + 1

    M = {}
    for iterations in range(10):
        # random walk function setup
        k = 0
        while 2 ** k < N:
            r = randrange(1, N)
            M[k] = (r, r * g)
            k += 1

        # first random walk
        H = ub * g
        c = ub
        for i in range(N):
            r, e = M[hash(H) % k]
            H = H + e
            c += r

        ori = H

        # second random walk
        H = a
        d = 0
        while c - d >= lb:
            if ub > c - d and H == ori:
                return c - d
            r, e = M[hash(H) % k]
            H = H + e
            d += r

    return discrete_log_bound_brute(a, g, bounds)


def discrete_log_bound_brute(a, g, bounds):
    """
    Find the discrete log of a under base g within bounds using brute force

    :param a: Target element
    :param g: Base element
    :param bounds: Bounds for discrete log search
    :return: Discrete log of a under base g
    """
    cul = bounds[0] * g
    for i in range(bounds[1] - bounds[0] + 1):
        if cul == a:
            ans = i + bounds[0]
            return ans
        cul = (cul + g)
    raise Exception(f"Discrete log for {a} under base {g} not found in bounds ({bounds[0]}, {bounds[1]})")

if __name__ == "__main__":

    # Step 1: Pick a prime order q (the group size)
    q = randprime(5,7)#randprime(10**2, 10**3)  # A prime between 100 and 1000
    print(f"Prime order q: {q}")

    # Step 2: Find a prime p such that q divides p-1 (p will be our modulus)
    p = q + 1
    while not isprime(p):
        p += q  # Increment by q until p is prime (ensures q divides p-1)
    print(f"Modulus p: {p}, p-1: {p-1}")

    # Step 3: Find a generator g of order q
    # First, get a generator of Z_p^* (order p-1)
    g_full = primitive_root(p)
    # Raise it to (p-1)/q to get an element of order q
    g = pow(g_full, (p-1)//q, p)
    print(f"Generator g: {g}")

    # Verify: g^q mod p should be 1, and no smaller power should be
    assert pow(g, q, p) == 1, "g^q != 1"
    for k in range(1, q):
        assert pow(g, k, p) != 1, f"g has order < q at k={k}"
    print(f"Group is cyclic of order {q} with generator {g}")

    n_C = 3 # number of clients
    data = [[1] for _ in range(n_C)]
    print(f'data: {data}')

    # step a
    private_nums = [max(1, randbelow(q)) for _ in range(n_C)] # step a
    print(f'private_nums: {private_nums}')

    # step b (skipped)

    # step c
    gy = []

    for sat_num in range(n_C):
        left = 0
        right = 0
        for j in range(n_C):
            if j < sat_num:
                left  += private_nums[j]
            elif j > sat_num:
                right  += private_nums[j]
      
        my_sum = left-right
        print(f'{left}-{right}= {my_sum}')
        gyi = g**my_sum
        print(f'gyi: {gyi}')
        gy.append(gyi)
    
    print(f'g^y: {gy}')
                
    # Step d
    secret_keys = [max(1,randbelow(q)) for _ in range(n_C)]

    print(f'secret keys: {secret_keys}')

    subset_aggregation_keys = []
    for i in range(n_C):
        num = (g **secret_keys[i])  * (gy[i]** private_nums[i])
        subset_aggregation_keys.append(num)

    print(f'subset agg. keys: {subset_aggregation_keys}')
    
    
    # Step e
    aggregation_key = 1 # a.k.a AK_AS

    for i in range(n_C):
        aggregation_key *= subset_aggregation_keys[i]

    print(f'agg. key {aggregation_key}')

    check_agg = g ** (sum(secret_keys))

    if (aggregation_key == check_agg):
        print('Aggregation key is correct')
    else:
        print('Aggregation key is incorrect)')

    # Step 2

    cipher_data = []
    
    for i in range(n_C):
        enc_data = g**(secret_keys[i] + data[i][0])
        cipher_data.append(enc_data)

    print(f'enc data: {cipher_data}')

    # step 3
    agg_model_param: int

    exp_sum = sum(cipher_data)

    agg_model = g**exp_sum
    print(f'agg. model: {agg_model}')
    print(f'num digits: {len(str(agg_model))}')

    result = discrete_log_bound(agg_model, g, (0,10000000000000000))

    print(f'result: {result}')