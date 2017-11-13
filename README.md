# DLM
Dual-Monolingual Language Model

Requirements:

1. Train, Dev and Test files with 1 utterance per line

2. SRILM directory

How to run:

1. Change the SRILM_ROOT variable in path.sh with your srilm directory

2. Run the calc_ppl.sh script with the following arguments:

arg1: train file

arg2: dev file

arg3: test file

The perplexity results will be printed on the console

(NOTE - Default settings run for ENG-MAN code-switched text. For running other settings, you may have to manually change specific language identification code (they have been commented with "NOTE") in clean_for_lm.py and compute_DLM_ppl.py)
