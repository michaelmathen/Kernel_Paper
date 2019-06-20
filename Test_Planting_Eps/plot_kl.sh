python3 ./plotter.py --filenames eps_annuli_test_0.05_.csv eps_annuli_test_0.1_.csv eps_annuli_test_0.2_.csv eps_annuli_test_0.4_.csv eps_rk_*.csv eps_d_*.csv --labels "annuli .05" "annuli .1" "annuli .2" "annuli .4" "Kuldorff Disk" "Discrepancy disk" --x n --y kl_div --smooth 2 --noline --x_name "Net size" --y_name "KL Divergence" --save kl.pdf
