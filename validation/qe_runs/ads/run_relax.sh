export PATH=$HOME/miniforge3/envs/qe/bin:$PATH
cd "/mnt/c/Users/Andre/Proyectos doctorado/simcert-suite/catcert/validation/qe_runs/ads"
for n in relax_clean relax_H relax_clean_d3 relax_H_d3; do mpirun -np 8 pw.x -in $n.in > $n.out 2>&1; done
echo done > DONE_RELAX
