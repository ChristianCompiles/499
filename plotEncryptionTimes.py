import matplotlib.pyplot as plt

with open("encryptDataTimes.txt", "r") as f:
    for i, line in enumerate(f):

        if i == 0:
            list_num_strs = line.split(',')
            num_params = [int(sat) for sat in list_num_strs]
            print(num_params)
        elif 1 == 1:
            list_time_strs = line.split(',')
            enc_times = [float(time) for time in list_time_strs]
            print(enc_times)
            pass


    plt.loglog(num_params, enc_times)
    plt.xlabel("Number of Parameters")
    plt.xticks(num_params)  # set exact x-tick locations
    plt.ylabel("Encryption Time (ms)")
    plt.title("Encryption Time vs Number of Satellites\n(log-log)")
    plt.grid(True)
    plt.show()