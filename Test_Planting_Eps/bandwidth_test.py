import partial_testing
import paths
import random

if __name__ == "__main__":


    pts = paths.load_philly()

        #seed = random.randint(0, 10000000)

    for kernel_name in [ "kernel_fast", "kernel_prune", "kernel_adaptive","kernel", "kernel2"]:
        for seed in [6100525, 3028580, 860284, 3211903, 5482194, 8679345, 800508, 2015356, 7756588, 9644922,
                         4470687, 3773279, 7190674, 423264, 1934284, 1084229, 8310557, 3532236, 3722290, 7638748]:

            partial_testing.testing_bandwidth_framework(
                pts,
                "bandwidth_{}_test.csv".format(kernel_name),
                1.0,
                -2.0,
                20,
                r=.05,
                p=.8,
                q=.5,
                algorithm=kernel_name,
                seed=seed,
                power_test=None)

        # for sat_meth in ["satscan_grid"]:#, "satscan_points"]:
        #     partial_testing.testing_partial_framework(
        #         pts,
        #         "eps_{}_test.csv".format(sat_meth),
        #         -1,
        #         -1.7,
        #         10,
        #         r=.05,
        #         p=.8,
        #         q=.5,
        #         algorithm=sat_meth,
        #         statistic="k",
        #         seed=seed,
        #         power_test=None)

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
        #     "eps_rk_disk_test.csv",
        #     -1,
        #     -1.7,
        #     10,
        #     r=.05,
        #     p=.8,
        #     q=.5,
        #     algorithm="combinatorial",
        #     statistic="k",
        #     seed=seed,
        #     power_test=None)
        # #
        # partial_testing.testing_partial_framework(
        #     pts,
        #     "eps_d_disk_test.csv",
        #     -1,
        #     -1.7,
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
