export PATH=$HOME/miniforge3/envs/qe/bin:$PATH
cd "/mnt/c/Users/Andre/Proyectos doctorado/simcert-suite/catcert/validation/qe_runs/conv"
while [ ! -f DONE_VAC3 ]; do sleep 30; done
mpirun -np 8 pw.x -in al111_11L_vac8b.in > al111_11L_vac8b.out 2>&1
echo done > DONE_VAC4
