import pstats

p = pstats.Stats("profile.pstat")
p.sort_stats("tottime").print_stats(100)  # Print top 20 functions by total time
