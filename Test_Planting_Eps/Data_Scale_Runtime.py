import partial_testing
import paths
import random
import pyscan

if __name__ == "__main__":

    MAX_TIME=1000
    NUM_RUNS=30
    R_VAL = .01
    pts = paths.load_chicago()

    seed = 6100525
    # for sat_meth in ["satscan_grid"]:
    #     partial_testing.testing_partial_framework(
    #         pts,
    #         "runtime_{}_test.csv".format(sat_meth),
    #         -1,
    #         -3,
    #         NUM_RUNS,
    #         r=R_VAL,
    #         p=.8,
    #         q=.5,
    #         algorithm=sat_meth,
    #         statistic="b",
    #         seed=seed,
    #         power_test=None,
    #         max_time=MAX_TIME)
    #
    # partial_testing.testing_partial_framework(
    #     pts,
    #     "runtime_b_disk_test.csv",
    #     -1,
    #     -3,
    #     NUM_RUNS,
    #     r=R_VAL,
    #     p=.8,
    #     q=.5,
    #     algorithm="combinatorial",
    #     statistic="b",
    #     seed=seed,
    #     power_test=None,
    #     ,max_time=MAX_TIME)

    #,3028580,
    for seed in [6100525, 3028580, 860284]:#, 3211903, 5482194, 8679345, 800508, 2015356, 7756588, 9644922, 4470687, 3773279, 7190674, 423264, 1934284, 1084229, 8310557, 3532236, 3722290, 7638748]:

        #seed = random.randint(0, 10000000)

        # for kernel_name in ["kernel_fast"]:
            # partial_testing.testing_partial_framework(
            #     pts,
            #     "runtime_{}_test.csv".format(kernel_name),
            #     -1.0,
            #     -3,
            #     NUM_RUNS,
            #     r=R_VAL,
            #     p=.8,
            #     q=.5,
            #     algorithm=kernel_name,
            #     seed=seed,
            #     power_test=None,
            #     max_time=MAX_TIME)

        # for sat_meth in ["satscan_grid"]:
            # partial_testing.testing_partial_framework(
            #     pts,
            #     "runtime_{}_test.csv".format(sat_meth),
            #     -1,
            #     -3,
            #     NUM_RUNS,
            #     r=R_VAL,
            #     p=.8,
            #     q=.5,
            #     algorithm=sat_meth,
            #     statistic="b",
            #     seed=seed,
            #     power_test=None,
            #     max_time=MAX_TIME)

        partial_testing.testing_partial_framework(
            pts,
            "runtime_b_disk_test.csv",
            -1,
            -3,
            NUM_RUNS,
            r=R_VAL,
            p=.8,
            q=.5,
            algorithm="combinatorial",
            statistic="b",
            seed=seed,
            max_time=MAX_TIME,
            power_test=None)

        # partial_testing.testing_partial_framework(
        #     pts,
        #     "eps_kernel_test.csv",
        #     -1,
        #     -1.7,
        #     10,
        #     r=.05,
        #     p=.8,
        #     q=.5,
        #     algorithm="kernel",
        #     seed=seed,
        #     power_test=None)



        # partial_testing.testing_partial_framework(
        #     pts,
        #     "runtime_rk_disk_test.csv",
        #     -1,
        #     -3,
        #     NUM_RUNS,
        #     r=R_VAL,
        #     p=.8,
        #     q=.5,
        #     algorithm="combinatorial",
        #     statistic="k",
        #     seed=seed,
        #     power_test=None,
        #     max_time=MAX_TIME)
        #
        # partial_testing.testing_partial_framework(
        #     pts,
        #     "eps_d_disk_test.csv",
        #     -1,
        #     -2,
        #     10,
        #     r=.05,
        #     p=.8,
        #     q=.5,
        #     algorithm="combinatorial",
        #     statistic="d",
        #     seed=seed,
        #     power_test=None)
    # for i in [.2, .1, .05]:
    #     partial_testing.testing_partial_framework(
    #         pts,
    #         "eps_annuli_test_{}_.csv".format(i),
    #         -1.2,
    #         -2.3,
    #         50,
    #         r=.1,
    #         p=.8,
    #         q=.5,
    #         annuli_eps=i,
    #         algorithm="annuli",
    #         power_test=None)
    #

    # #

    # #
    # partial_testing.testing_partial_framework(
    #     pts,
    #     "eps_b_disk_test.csv",
    #     -1.2,
    #     -2.3,
    #     20,
    #     r=.1,
    #     p=.8,
    #     q=.5,
    #     algorithm="combinatorial",
    #     statistic="b",
    #     power_test=None)
