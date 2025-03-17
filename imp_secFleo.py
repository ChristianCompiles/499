from charm.toolbox.ecgroup import ECGroup, ZR
from charm.toolbox.eccurve import prime192v1
from secrets import randbelow
from random import randrange
from math import isqrt
from sage.all import discrete_log, GF

RED = '\033[31m'
RESET = '\033[0m'

#import gmpy2
# from functools import reduce
# import gmpy2
# , is_prime, mpz_random
# #import math
# #from typing import Optional
# from sympy import isprime, nextprime, primitive_root, randprime
# import random
# import hashlib
# import time

# def discrete_log_bound(target, gen, bounds):
#     """
#     Find the discrete log of a under base g within bounds using Pollard's Kangaroo algorithm

#     :param a: Target element
#     :param g: Base element
#     :param bounds: Bounds for discrete log search
#     :return: Discrete log of a under base g
#     """
#     a = int(target)
#     g = int(gen)
#     width = bounds[1] - bounds[0]
#     if width < 1000:
#         return discrete_log_bound_brute(a, g, bounds)

#     lb = bounds[0]
#     ub = bounds[1]

#     N = isqrt(width) + 1

#     M = {}
#     for iterations in range(10):
#         # random walk function setup
#         k = 0
#         while 2 ** k < N:
#             #print("here 1")
#             r = randrange(1, N)
#             M[k] = (r, r * g)
#             k += 1

#         # first random walk
#         H = ub * g
#         c = ub
#         for i in range(N):
#             r, e = M[hash(int(H)) % k]
#             H = H + e
#             c += r
#             #print("here 2")

#         ori = H

#         # second random walk
#         H = a
#         d = 0
#         while c - d >= lb:
#             if ub > c - d and H == ori:
#                 return c - d
#             r, e = M[hash(H) % k]
#             H = H + e
#             d += r

#     return discrete_log_bound_brute(a, g, bounds)

# def discrete_log_bound_brute(a, g, bounds):
#     """
#     Find the discrete log of a under base g within bounds using brute force

#     :param a: Target element
#     :param g: Base element
#     :param bounds: Bounds for discrete log search
#     :return: Discrete log of a under base g
#     """
#     cul = bounds[0] * g
#     for i in range(bounds[1] - bounds[0] + 1):
#         if cul == a:
#             ans = i + bounds[0]
#             return ans
#         cul = (cul + g)
#     raise Exception(f"Discrete log for {a} under base {g} not found in bounds ({bounds[0]}, {bounds[1]})")

if __name__ == "__main__":

    group = ECGroup(prime192v1)
    q = 5 #group.order() # get the order. or use 5

    print(f'\norder: {q}\n')
    g = 4 # group.random() # random generator. or use 4
    print(f'generator: {g}\n')

    n_C = 3 # number of clients (each client is in its own orbit)
    data = [[1] for _ in range(n_C)]
    print(f'data: {data}\n')

    # step a
    private_nums = [randbelow(int(q)) for _ in range(n_C)] # step a
    print(f'private_nums: {private_nums}\n')

    # step b
    public_keys = [g**p_n for p_n in private_nums] # not using these values since using reduced equation

    # step c
    gy_original = [] # shared keys using original method
    gy_reduced = [] # shared keys using reduced method   
    yi = [] # powers of shared key base 

    for sat_num in range(n_C):
        left = 0
        right = 0
        for j in range(n_C):
            if j < sat_num:
                left += private_nums[j]
            elif j > sat_num:
                right += private_nums[j]
      
        my_sum = left-right
        yi.append(my_sum)
        print(f'{left} - {right} =\n{my_sum}')
        gyi = g**my_sum
        print(f'gyi_reduced: {gyi}\n')
        gy_reduced.append(gyi)

    print(f'g^y: {gy_reduced}\n')

    for sat_num in range(n_C):
        numerator = 1
        denominator = 1
        for j in range(n_C):
            if j < sat_num:
                numerator *= g**private_nums[j]
            elif j > sat_num:
                denominator *= g**private_nums[j]

        division = numerator / denominator
        print(f'{numerator} / {denominator} =\n{division}')
        
        gy_original.append(division)
        print(f'gyi_original: {gy_original[sat_num]}\n')
    
    # compare original vs reduced:
    assert gy_original == gy_reduced, "should have same shared key derivation"
                
    # Step d
    secret_keys = [randbelow(int(q)) for _ in range(n_C)]#[max(1,randbelow(int(q))) for _ in range(n_C)]
    print(f'secret keys: {secret_keys}\n')

    prop_1_check = sum([private_nums[i]*yi[i] for i in range(n_C)] )

    assert prop_1_check == 0, "according to prop_1, should be 0"

    partial_agg_key = []
    for i in range(n_C):
        num = g** (secret_keys[i] + (private_nums[i] * yi[i]))    #(g ** secret_keys[i])  * (gy[i] ** private_nums[i])
        partial_agg_key.append(num)

    print(f'subset agg. keys: {partial_agg_key}\n')
    
    # Step e
    aggregation_key = 1 # a.k.a AK_AS

    for i in range(n_C):
        aggregation_key *= partial_agg_key[i]

    print(f'agg. key {aggregation_key}\n')

    check_agg = g ** (sum(secret_keys))

    print(f'check_agg: {check_agg}')

    assert aggregation_key == check_agg, "aggregation key is incorrect"

    # Step 2

    cipher_data = []
    
    for i in range(n_C):
        enc_data = g**(secret_keys[i] + data[i][0])
        cipher_data.append(enc_data)

    print(f'enc data: {cipher_data}')

    # step 3
    agg_model_param: int

    exp_sum = sum(cipher_data)
    print(f'exp_sum: {exp_sum}')

    agg_model = g**exp_sum
    print(f'agg. model: {agg_model}')
    print(f'num digits: {len(str(agg_model))}')

    # width1 = 10000000000000000000
    # width2 = 100000000000000000

    # print(f'width: {width1-width2}')
    result = discrete_log(GF(q)(agg_model), GF(q)(g)) #discrete_log_bound(16, 2, (0, 10))

    print(f'result: {result}')