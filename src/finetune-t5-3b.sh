#!/bin/bash

CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 python3 t5-finetune.py  --batch_size 16 --stepsize 10000 --nsteps 1000000  --data_dir data --model_name 3B
