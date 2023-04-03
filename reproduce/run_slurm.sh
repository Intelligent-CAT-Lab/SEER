rm job_ids
declare JOB0=$(sbatch rq1_reproduce/rq1.slurm;)
declare JOB1=$(sbatch rq2_reproduce/rq2.slurm;)
declare JOB2=$(sbatch rq3_reproduce_attn_threshold/rq3_1.slurm;)
declare JOB3=$(sbatch rq3_reproduce_attn_weights/rq3_2.slurm;)
declare JOB4=$(sbatch rq3_reproduce_embeddings/rq3_3.slurm;)

echo "${JOB0}" >> './job_ids';
echo "${JOB1}" >> './job_ids';
echo "${JOB2}" >> './job_ids';
echo "${JOB3}" >> './job_ids';
echo "${JOB4}" >> './job_ids';

cat ./job_ids;
