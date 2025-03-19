from charm.toolbox.ecgroup import ECGroup, ZR
from charm.toolbox.eccurve import prime192v1
from secrets import randbelow
#from random import randrange
#from sage.all import discrete_log, GF
import math
import time


if __name__ == "__main__":

    #group = ECGroup(prime192v1)
    q = 5 #group.order() # ORDER

    print(f'\norder: {q}')
    g = 4 # group.random() # GENERATOR
    print(f'generator: {g}')

    n_C = 5 # number of clients (each client is in its own orbit)
    data = [[0.7] for _ in range(n_C)]
    print(f'data: {data}\n')

    # step a
    private_nums =  [3 for _ in range(n_C)] # step a
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
        #print(f'{left} - {right} =\n{my_sum}')
        gyi = g**my_sum
        #print(f'gyi_reduced: {gyi}\n')
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
        #print(f'{numerator} / {denominator} =\n{division}')
        
        gy_original.append(division)
        #print(f'gyi_original: {gy_original[sat_num]}\n')
    
    # compare original vs reduced:
    assert gy_original == gy_reduced, "should have same shared key derivation"
                
    # Step d
    secret_keys = [2 for _ in range(n_C)]
    print(f'secret keys: {secret_keys}\n')

    prop_1_check = sum([private_nums[i]*yi[i] for i in range(n_C)] )

    assert prop_1_check == 0, "according to prop_1, should be 0"

    partial_agg_key = []
    for i in range(n_C):
        num = g** (secret_keys[i] + (private_nums[i] * yi[i]))
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
    
    start_enc_time = time.time()
    for i in range(n_C):
        enc_data = g**(secret_keys[i] + data[i][0])
        cipher_data.append(enc_data)

    end_enc_time = time.time()

    print(f'time to encrypt {len(data)} data: {end_enc_time - start_enc_time}sec')

    print(f'enc data: {cipher_data}')

    # step 3c
    agg_model_param: int

    exp_sum = sum(cipher_data)
    print(f'exp_sum: {exp_sum}')

    weighted_agg = math.prod(cipher_data) / aggregation_key
    print(f'before finding exp and averaging: {weighted_agg}')

    exp = math.log(weighted_agg, g)#  discrete_log(GF(q)(weighted_agg), GF(q)(g))
    print(f'the exp is: {exp}')

    exp_avg = exp / len(data)
    print(f'the average of the data is: {exp_avg}')
    