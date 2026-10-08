export PATH=$HOME/miniforge3/envs/qe/bin:$PATH
cd "/mnt/c/Users/Andre/Proyectos doctorado/simcert-suite/catcert/validation/qe_runs/conv"
for n in al111_5L_k24 al111_5L_k32 al111_9L al111_11L; do
  mpirun -np 8 pw.x -in $n.in > $n.out 2>&1
done
echo done > DONE
