#!/bin/bash

experiments=(reptodem demtorep racism vaccines moonlanding sexism)
nexperiments=${#experiments[@]}

checkpoints=(1010000 1020000  1030000  1040000  1050000  1060000  1070000 1080000 1090000 1100000)
checkpoints=($(seq 1010000 10000 1100000))
ncheckpoints=${#checkpoints[@]}

gpus=(8 9 10 11 12 13 14 15)
ngpus=${#gpus[@]}
GPUIX=0


for ((iter1=0;iter1 < $nexperiments;iter1++))
do
    EXPERIMENT=${experiments[$iter1]}
    for ((iter2=0;iter2 < $ncheckpoints;iter2++))
    do
        CHECKPOINT=${checkpoints[$iter2]}
        GPU=${gpus[$GPUIX]}
        comm="CUDA_VISIBLE_DEVICES=$GPU python3 setup_t5_and_predict.py --ckpt $CHECKPOINT --experiment  $EXPERIMENT --model_dir models-t5/3B --temperature 0.7 &"
        eval $comm
        echo $comm
        GPUIX=$(($GPUIX + 1))
        if [ $GPUIX -eq $ngpus ]
        then
            echo "waiting at $GPU\n\n"
            wait
            GPUIX=0
        else
            :
        fi
    done
done

