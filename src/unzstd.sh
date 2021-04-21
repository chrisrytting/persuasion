#!/bin/bash
#This is a script specifically for unzipping all 00-29 .zst files in the pile
#training data


for i in {0..9}
do
    comd="zstd -d 0$i.jsonl.zst &"
    echo $comd
    exec $comd
done


for i in {10..29}
do
    comd="zstd -d $i.jsonl.zst &"
    echo $comd
    exec $comd
done
