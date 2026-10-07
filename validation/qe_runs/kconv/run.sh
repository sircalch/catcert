export PATH=$HOME/miniforge3/envs/qe/bin:$PATH
cd "/mnt/c/Users/Andre/Proyectos doctorado/simcert-suite/catcert/validation/qe_runs/kconv"
for k in 16 24 32; do mpirun -np 8 pw.x -in albulk_k$k.in > albulk_k$k.out 2>&1; done
echo done > DONE
