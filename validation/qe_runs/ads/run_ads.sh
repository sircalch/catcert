export PATH=$HOME/miniforge3/envs/qe/bin:$PATH
cd "/mnt/c/Users/Andre/Proyectos doctorado/simcert-suite/catcert/validation/qe_runs/ads"
for n in H2_box clean_2x2 H_2x2 H2_box_d3 clean_2x2_d3 H_2x2_d3; do
  mpirun -np 8 pw.x -in $n.in > $n.out 2>&1
done
echo done > DONE_ADS
