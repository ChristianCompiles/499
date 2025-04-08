from charm.toolbox.ecgroup import ECGroup #, ZR
from charm.toolbox.eccurve import secp224k1 # prime192v1, prime239v1, 
import secrets
import math
import time
import numpy
import mpmath

if __name__ == "__main__":

    TESTING_BIG = False

    if TESTING_BIG is True:
        group = ECGroup(secp224k1) #ECGroup(prime192v1)
        q = mpmath.mpf(str(group.order()))
        g = mpmath.mpf(str(group.random()))
    else:
        q = mpmath.mpf(2**50) # 51
        g = mpmath.mpf(2**224) # 224

    print(f'\norder: {q}')
    print(f'generator: {g}')

    n_C = 10 # number of clients (each client is in its own orbit)
    data = [mpmath.mpf(0.75) for _ in range(n_C)] # numpy.random.rand(n_C) # 
    print(f'data: {data}\n')

    # step a
    x_in = [mpmath.mpf(max(float(1), float(secrets.randbelow(int(q))))) for _ in range(n_C)]

    print(f'x_in: {x_in}\n')

    # step b

    timea = time.time()
    public_keys = [g**p_n for p_n in x_in]
    
    # step c
    gy_original = [] # shared keys using original method
    #gy_reduced = [] # shared keys using reduced method   
    #yi = [] # powers of shared key base 

    # for sat_num in range(n_C):
    #     left = 0
    #     right = 0
    #     for j in range(n_C):
    #         if j < sat_num:
    #             left += x_in[j]
    #         elif j > sat_num:
    #             right += x_in[j]
      
    #     my_sum = left-right
    #     yi.append(my_sum)
        #print(f'{left} - {right} =\n{my_sum}')
        #gyi = g**my_sum
        #print(f'gyi_reduced: {gyi}\n')
        #gy_reduced.append(gyi)

    #print(f'g^y reduced: {gy_reduced}\n')

    for sat_num in range(n_C):
        numerator = mpmath.mpf(1.0)
        denominator = mpmath.mpf(1.0)
        for j in range(n_C):
            if j < sat_num:
                numerator *= public_keys[j]
            elif j > sat_num:
                denominator *= public_keys[j]

        division = numerator / denominator
        #print(f'{numerator} / {denominator} =\n{division}')
        
        gy_original.append(division)
    print(f'gyi original: {gy_original}\n')
    
    # compare original vs reduced:
    # for i in range(n_C):
    #     if gy_original[i] == gy_reduced[i]:
    #         symbol = "=="
    #     else:
    #         symbol = "!="
    #     print(f'{gy_original[i]} {symbol} {gy_reduced[i]}')
    
    #assert gy_original == gy_reduced, "should have same shared key derivation"
                
    # Step d
    secret_keys = [mpmath.mpf(max(1, secrets.randbelow(int(q)))) for _ in range(n_C)]
    print(f'secret keys: {secret_keys}\n')

    # prop_1_check = sum([x_in[i]*yi[i] for i in range(n_C)] )

    # assert prop_1_check == 0, "according to prop_1, should be 0"

    partial_agg_key = []
    for i in range(n_C):
        key = (g**secret_keys[i]) * (gy_original[i] ** x_in[i])
        partial_agg_key.append(key)

    print(f'subset agg. keys: {partial_agg_key}\n')
    
    # Step f
    # a.k.a AK_AS
    aggregation_key = math.prod(partial_agg_key)

    timeb = time.time()

    print(f'agg. key {aggregation_key}\n')
    print(f'time to make keys: {timeb-timea}')

    # check_agg = g ** (sum(secret_keys))

    # print(f'check_agg: {check_agg}')

    #assert aggregation_key == check_agg, "aggregation key is incorrect"

    # Step 2

    cipher_data = []
    
    start_enc_time = time.time()

    for i in range(n_C):
        enc_data = g**(secret_keys[i] + mpmath.mpf(data[i]))
        cipher_data.append(enc_data)

    end_enc_time = time.time()

    print(f'time to encrypt {len(data)} data: {end_enc_time - start_enc_time}sec')

    print(f'enc data: {cipher_data}')

    # step 3c
    #agg_model_param: int

    exp_sum = sum(cipher_data)
    print(f'exp_sum: {exp_sum}')

    product = math.prod(cipher_data)
    print(f"product: {product}")
    weighted_agg = product / aggregation_key
    print(f'before finding exp and averaging: {weighted_agg}')
    
    exp = mpmath.log(weighted_agg, g)
    print(f'the exp is: {exp}')

    print(f"length of the data: {len(data)}")
    exp_avg = mpmath.mpf(exp) / mpmath.mpf(len(data))
    print(f'the average of the data is: {exp_avg}')
    