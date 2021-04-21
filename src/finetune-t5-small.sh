#!/bin/bash

CUDA_VISIBLE_DEVICES=8,9,10,11 python3 t5-finetune.py  --batch_size 128 --stepsize 100000 --nsteps 1000000  --data_dir /persuasion/data/data --model_name small --from_model
