import datetime
import shutil
import functools
import json
import os
import re
import pprint
import random
import string
import sys
import tensorflow as tf
import glob
import argparse
import warnings
import t5
import tensorflow as tf
import tensorflow_datasets as tfds
import time
from contextlib import contextmanager
import logging as py_logging
import gzip
import json

parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', type=int, default = 1)
parser.add_argument('--lr', type=float, default=0.003)
parser.add_argument('--stepsize', type = int, default = 100)
parser.add_argument('--nsteps', type = int, default=1000)
parser.add_argument('--data_dir', type = str, default='data')
parser.add_argument('--model_name', type = str)
parser.add_argument('--from_model', action='store_true', default = False)
args = parser.parse_args()
GPUS = os.environ['CUDA_VISIBLE_DEVICES'].split(',')
NGPUS = len(GPUS)

BASE_DIR = "."  # @param { type: "string" }
DATA_DIR = os.path.join(BASE_DIR, args.data_dir)
MODELS_DIR = os.path.join(BASE_DIR, "models-t5")
ON_CLOUD = False


warnings.filterwarnings("ignore", category=DeprecationWarning)


# Improve logging.


@contextmanager
def tf_verbosity_level(level):
    og_level = tf.compat.v1.logging.get_verbosity()
    tf.compat.v1.logging.set_verbosity(level)
    yield
    tf.compat.v1.logging.set_verbosity(og_level)



jsonfiles=sorted(glob.glob(os.path.join(DATA_DIR,"*.jsonl")))
trainfiles = jsonfiles[:-1]
valfiles = jsonfiles[-1]

# =====================For converting JSONL to tfds===========================
fib_counts_path = os.path.join(DATA_DIR, "fib-counts.json")
fib_json_path = {
    "train": trainfiles,
    "validation": valfiles,
}

def fib_dataset_fn(split, shuffle_files=False):
    """
    Convert jsons into tfds
    """
    #print(f"\n\nHERE{ds}\n\n")

    ds = tf.data.TextLineDataset(fib_json_path[split])


    def f(tnsr):
        try:
            text = eval(tnsr.numpy())['text']
            text = tf.constant(text)
        except:
            text = ""
            text = tf.constant(text)
        #print(f'\n\n\n\nThis is the text\n{len(text),type(text)}\n\n\n\n\n\n')
        return text
        #return {'text':text}

    ds = ds.map(lambda x: tf.py_function(func=f,inp=[x], Tout=tf.string))

    ds = ds.map(lambda *ex: dict(zip(["text", "meta"], ex)))

    #ds = t5.data.preprocessors.fill_in_the_blank_sized(ds)
    return ds




t5.data.TaskRegistry.add(
    "fib",
    # Supply a function which returns a tf.data.Dataset.
    dataset_fn=fib_dataset_fn,
    splits=["train", "validation"],
    # Supply a function which preprocesses text from the tf.data.Dataset.
    text_preprocessor=[t5.data.preprocessors.fill_in_the_blank_sized],
    # Use the same vocabulary that we used for pre-training.
    #sentencepiece_model_path=t5.data.DEFAULT_SPM_PATH,
    # Lowercase targets before computing metrics.
    postprocess_fn=t5.data.postprocessors.lower_text,
    # We'll use accuracy as our evaluation metric.
    metric_fns=[t5.evaluation.metrics.accuracy],
    # Not required, but helps for mixing and auto-caching.
    #num_input_examples=num_atr_examples,
)

fib_task = t5.data.TaskRegistry.get("fib")
ds = fib_task.get_dataset(
    split="validation",
    sequence_length={"inputs": 10, "targets": 10}
)
print("A few preprocessed validation examples...")
for ex in tfds.as_numpy(ds.take(5)):
    print(ex)


MODEL_SIZE = args.model_name  # @param["small", "base", "large", "3B", "11B"]
# Public GCS path for T5 pre-trained model checkpoints
BASE_PRETRAINED_DIR = os.path.join(BASE_DIR, "base-t5")
PRETRAINED_DIR = os.path.join(BASE_PRETRAINED_DIR, MODEL_SIZE)

if ON_CLOUD and MODEL_SIZE == "3B":
    tf.logging.warn(
        "The `3B` model is too large to use with the 5GB GCS free tier. "
        "Make sure you have at least 25GB on GCS before continuing."
    )
elif ON_CLOUD and MODEL_SIZE == "11B":
    raise ValueError(
        "The `11B` parameter is too large to fine-tune on the `v2-8` TPU "
        "provided by Colab. Please comment out this Error if you're running "
        "on a larger TPU."
    )

# Set parallelism and batch size to fit on v2-8 TPU (if possible).
# Limit number of checkpoints to fit within 5GB (if possible).
model_parallelism, train_batch_size, keep_checkpoint_max = {
    "small": (NGPUS, 256, 16),
    "base": (2, 128, 8),
    "large": (8, 64, 4),
    "3B": (NGPUS, 1, 1),
    "11B": (8, 16, 1),
}[MODEL_SIZE]

batch_parallelism = 1

# ==================================================

# ==================================================

MODEL_DIR = os.path.join(MODELS_DIR, args.model_name)
tf.io.gfile.makedirs(MODEL_DIR)

#tf.io.gfile.makedirs(os.path.join(MODEL_DIR,'data'))
#for filename in glob.glob(os.path.join(DATA_DIR, '*.*')):
#    shutil.copy(filename, os.path.join(MODEL_DIR, 'data'))




# The models from our paper are based on the Mesh Tensorflow Transformer.
model = t5.models.MtfModel(
    model_dir=MODEL_DIR,
    tpu=None,
    mesh_shape=f"model:{model_parallelism},batch:{batch_parallelism}",
    mesh_devices=[f"gpu:{ix}" for ix in range(NGPUS)],
    batch_size=args.batch_size,
    sequence_length={"inputs": 250, "targets": 250},
    learning_rate_schedule=args.lr,
    save_checkpoints_steps=args.stepsize,
    iterations_per_loop=100,
)


import tensorboard as tb

tb.notebook.start("--logdir " + MODELS_DIR)

FINETUNE_STEPS = args.nsteps  # @param {type: "integer"}
import numpy as np

if args.from_model:
    PRETRAINED_DIR = MODEL_DIR

model.finetune(
    mixture_or_task_name="fib",
    pretrained_model_dir=PRETRAINED_DIR,
    finetune_steps=FINETUNE_STEPS,
)
