export PATH=$HOME/miniforge3/envs/qe/bin:$PATH
cd "/mnt/c/Users/Andre/Proyectos doctorado/simcert-suite/catcert/validation/qe_runs/conv"
for n in al111_7L_vac4 al111_7L_vac8; do mpirun -np 8 pw.x -in $n.in > $n.out 2>&1; done
echo done > DONE_VAC
