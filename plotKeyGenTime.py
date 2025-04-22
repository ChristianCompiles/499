import matplotlib.pyplot as plt

with open("data.txt", "r") as f:
    for i, line in enumerate(f):

        if i == 0:
            list_num_strs = line.split(',')
            num_sats = [int(sat) for sat in list_num_strs]
            print(num_sats)
        elif 1 == 1:
            list_time_strs = line.split(',')
            gen_times = [float(time) for time in list_time_strs]
            print(gen_times)
            pass


    plt.plot(num_sats, gen_times)
    plt.xlabel("Number of Satellites")
    plt.ylabel("Key Generation Time (ms)")
    plt.title("Key Generation Time vs Number of Satellites")
    plt.grid(True)
    plt.show()