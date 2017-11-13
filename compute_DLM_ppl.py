import os
import sys
import math

# Global dictionaries
unigram_logprob_lang1 = {}
bigram_logprob_lang1 = {}
trigram_logprob_lang1 = {}
unigram_backoff_lang1 = {}
bigram_backoff_lang1 = {}
logprob_ratios_lang1 = {}

unigram_logprob_lang2 = {}
bigram_logprob_lang2 = {}
trigram_logprob_lang2 = {}
unigram_backoff_lang2 = {}
bigram_backoff_lang2 = {}
logprob_ratios_lang2 = {}

# Check if word is Lang2
# NOTE - Add your default code for detection of language here
# (Now, it is set for Mandarin)
def isLang2( word ):

	if word == "":
		return 1

	if word[0] == "<":
		return 0

	start_bracs = [ '(', '[' ]
	if ord(word[0]) >= 123 and (word[0] not in start_bracs) :
		return 1
	elif word[0] in start_bracs and word != "()" and word != "[]":
		return isLang2(word[1:])
	else:
		return 0

# Check if word is Lang1
# NOTE - Add your default code for detection of language here
# (Now, it is set for English)
def isLang1( word ):

	if word == "":
		return 1

	if word[0] == "<":
		return 0

	start_bracs = [ '(', '[' ]
	if ord(word[0]) < 123 and (word[0] not in start_bracs):
		return 1
	elif word[0] in start_bracs and word != "()" and word != "[]":
		return isLang1(word[1:])
	else:
		return 0

def print_test_ppl(key, logprob, debug):

	if debug:
		print key + ": " + str(logprob)

def calc_ratios(lang):

	logprob_ratios = {}
	# backoff_ratios = {}
	logprob_total = 0
	# backoff_total = 0

	if lang == "lang1":
		for key in bigram_logprob_lang1:
			words = key.split("_")
			if words[0] == "<LANG2>" and isLang1(words[1]):
				logprob_ratios[words[1]] = pow(10,bigram_logprob_lang1[key])
				logprob_total += pow(10, bigram_logprob_lang1[key])
		logprob_ratios["<unk>"] = pow(10,unigram_logprob_lang1["<unk>"]+unigram_backoff_lang1["<LANG2>"])
		logprob_total += logprob_ratios["<unk>"]

	elif lang == "lang2":
		for key in bigram_logprob_lang2:
			words = key.split("_")
			if words[0] == "<LANG1>" and isLang2(words[1]):
				logprob_ratios[words[1]] = pow(10,bigram_logprob_lang2[key])
				logprob_total += pow(10, bigram_logprob_lang2[key])
		logprob_ratios["<unk>"] = pow(10,unigram_logprob_lang2["<unk>"]+unigram_backoff_lang2["<LANG1>"])
		logprob_total += logprob_ratios["<unk>"]

	for key in logprob_ratios:
		logprob_ratios[key] = logprob_ratios[key] / (logprob_total)

	return logprob_ratios

def get_start_prob( start_word, debug ):

	key = "<s>_" + start_word

	if isLang1(start_word):
		if key in bigram_logprob_lang1:
			print_test_ppl(key, bigram_logprob_lang1[key], debug)
			return bigram_logprob_lang1[key]
		elif start_word in unigram_logprob_lang1:
			print_test_ppl(start_word, unigram_logprob_lang1[start_word] + unigram_backoff_lang1["<s>"], debug)
			return unigram_logprob_lang1[start_word] + unigram_backoff_lang1["<s>"]
		else:
			print_test_ppl("<unk>", unigram_logprob_lang1["<unk>"] + unigram_backoff_lang1["<s>"], debug)
			return unigram_logprob_lang1["<unk>"] + unigram_backoff_lang1["<s>"]

	else:
		if key in bigram_logprob_lang2:
			print_test_ppl(key, bigram_logprob_lang2[key], debug)
			return bigram_logprob_lang2[key]
		elif start_word in unigram_logprob_lang2:
			print_test_ppl(start_word, unigram_logprob_lang2[start_word] + unigram_backoff_lang2["<s>"], debug)
			return unigram_logprob_lang2[start_word] + unigram_backoff_lang2["<s>"]
		else:
			print_test_ppl("<unk>", unigram_logprob_lang2["<unk>"] + unigram_backoff_lang2["<s>"], debug)
			return unigram_logprob_lang2["<unk>"] + unigram_backoff_lang2["<s>"]

def get_next_prob( prev2_word, prev_word, curr_word, debug ):

	global logprob_ratios_lang2
	global logprob_ratios_lang1

	# CHECK FOR BIGRAM

	# <s> / LANG1 - LANG1 / </s>
	if not isLang2(curr_word) and not isLang2(prev_word):
		key = prev_word + "_" + curr_word
		if key in bigram_logprob_lang1:
			print_test_ppl(key, bigram_logprob_lang1[key], debug)
			return bigram_logprob_lang1[key]

	# <s> / LANG2 - LANG2 / </s>
	elif not isLang1(curr_word) and not isLang1(prev_word):
		key = prev_word + "_" + curr_word
		if key in bigram_logprob_lang2:
			print_test_ppl(key, bigram_logprob_lang2[key], debug)
			return bigram_logprob_lang2[key]
	
	# LANG1 - LANG2
	elif isLang2(curr_word) and isLang1(prev_word):
		key = prev_word + "_<LANG2>"
		if key in bigram_logprob_lang1 and curr_word in logprob_ratios_lang2:
			actual_key = prev_word + "_" + curr_word
			print_test_ppl(actual_key, bigram_logprob_lang1[key] + math.log10(logprob_ratios_lang2[curr_word]), debug)
			return bigram_logprob_lang1[key] + math.log10(logprob_ratios_lang2[curr_word])

		elif key not in bigram_logprob_lang1 and curr_word in logprob_ratios_lang2:

			actual_key = prev_word + "_" + curr_word

			if prev_word in unigram_backoff_lang1:
				print_test_ppl(actual_key + "_case-1", unigram_logprob_lang1["<LANG2>"] + unigram_backoff_lang1[prev_word] + math.log10(logprob_ratios_lang2[curr_word]) , debug)
				return unigram_logprob_lang1["<LANG2>"] + unigram_backoff_lang1[prev_word] + math.log10(logprob_ratios_lang2[curr_word])
			else:
				print_test_ppl(actual_key + "_case-1", unigram_logprob_lang1["<LANG2>"] + math.log10(logprob_ratios_lang2[curr_word]) , debug)
				return unigram_logprob_lang1["<LANG2>"] +  math.log10(logprob_ratios_lang2[curr_word])
			

		elif key in bigram_logprob_lang1 and curr_word not in logprob_ratios_lang2:

			actual_key = prev_word + "_" + "<unk_lang2>"

			print_test_ppl(actual_key + "_case-2", bigram_logprob_lang1[key] + math.log10(logprob_ratios_lang2["<unk>"]) ,debug)
			return bigram_logprob_lang1[key] + math.log10(logprob_ratios_lang2["<unk>"])

		else:
			actual_key = prev_word + "_" + "<unk_lang2>"

			if prev_word in unigram_backoff_lang1:
				print_test_ppl(actual_key + "_case-3",unigram_logprob_lang1["<LANG2>"] + unigram_backoff_lang1[prev_word]  + math.log10(logprob_ratios_lang2["<unk>"]) ,debug)
				return unigram_logprob_lang1["<LANG2>"] + unigram_backoff_lang1[prev_word] + math.log10(logprob_ratios_lang2["<unk>"])			
			else:
				print_test_ppl(actual_key + "_case-3",unigram_logprob_lang1["<LANG2>"]   + math.log10(logprob_ratios_lang2["<unk>"]) ,debug)
				return unigram_logprob_lang1["<LANG2>"] + math.log10(logprob_ratios_lang2["<unk>"])			
			

	# LANG2 - LANG1
	elif isLang1(curr_word) and isLang2(prev_word):
		key = prev_word + "_<LANG1>"
		if key in bigram_logprob_lang2 and curr_word in logprob_ratios_lang1:
			actual_key = prev_word + "_" + curr_word
			print_test_ppl(actual_key, bigram_logprob_lang2[key] + math.log10(logprob_ratios_lang1[curr_word]), debug)
			return bigram_logprob_lang2[key] + math.log10(logprob_ratios_lang1[curr_word])

		elif key not in bigram_logprob_lang2 and curr_word in logprob_ratios_lang1:

			actual_key = prev_word + "_" + curr_word
			if prev_word in unigram_backoff_lang2:	
				print_test_ppl(actual_key + "_case-1", unigram_logprob_lang2["<LANG1>"]+unigram_backoff_lang2[prev_word] + math.log10(logprob_ratios_lang1[curr_word]), debug)
				return unigram_logprob_lang2["<LANG1>"] + unigram_backoff_lang2[prev_word] + math.log10(logprob_ratios_lang1[curr_word])
			else:
				print_test_ppl(actual_key + "_case-1", unigram_logprob_lang2["<LANG1>"]+ math.log10(logprob_ratios_lang1[curr_word]), debug)
				return unigram_logprob_lang2["<LANG1>"] + math.log10(logprob_ratios_lang1[curr_word])

		elif key in bigram_logprob_lang2 and curr_word not in logprob_ratios_lang1:

			actual_key = prev_word + "_" + "<unk_lang1>"

			print_test_ppl(actual_key + "_case-2", bigram_logprob_lang2[key] + math.log10(logprob_ratios_lang1["<unk>"]) ,debug)
			return bigram_logprob_lang2[key] + math.log10(logprob_ratios_lang1["<unk>"])

		else:
			actual_key = prev_word + "_" + "<unk_lang1>"
			
			if prev_word in unigram_backoff_lang2:	
				print_test_ppl(actual_key + "_case-3", unigram_logprob_lang2["<LANG1>"] + unigram_backoff_lang2[prev_word] + math.log10(logprob_ratios_lang1["<unk>"]) ,debug)
				return unigram_logprob_lang2["<LANG1>"] + unigram_backoff_lang2[prev_word] + math.log10(logprob_ratios_lang1["<unk>"])			
			else:
				print_test_ppl(actual_key + "_case-3", unigram_logprob_lang2["<LANG1>"] + math.log10(logprob_ratios_lang1["<unk>"]) ,debug)
				return unigram_logprob_lang2["<LANG1>"]  + math.log10(logprob_ratios_lang1["<unk>"])			
				

	if ((isLang2(curr_word) == isLang1(prev_word)) or (isLang1(curr_word) == isLang2(prev_word))) and (isLang2(curr_word) or isLang1(curr_word)) and (isLang2(prev_word) or isLang1(prev_word)) :
		assert (False), "Some Error Occured"

	# CHECK FOR UNIGRAM AND OOV NOW
	if isLang1(curr_word) or (curr_word == "</s>" and isLang1(prev_word)):
		key = curr_word
		
		if key in unigram_logprob_lang1:
			add = 0
			if isLang1(prev_word) and prev_word in unigram_backoff_lang1:
				add = unigram_backoff_lang1[prev_word]
			elif isLang2(prev_word) and prev_word in unigram_backoff_lang2:
				add = unigram_backoff_lang2[prev_word]
			print_test_ppl(key, unigram_logprob_lang1[key]+add, debug)
			return unigram_logprob_lang1[key]+add

		# OOV
		else:
			base = unigram_logprob_lang1["<unk>"]
			if isLang1(prev_word) and prev_word in unigram_backoff_lang1:
				base += unigram_backoff_lang1[prev_word]
			elif isLang2(prev_word) and prev_word in unigram_backoff_lang2:
				base += unigram_backoff_lang2[prev_word]
			print_test_ppl("<unk_lang1>", base, debug)
			return base

	else:
		key = curr_word

		if key in unigram_logprob_lang2:
			add = 0
			if isLang2(prev_word) and prev_word in unigram_backoff_lang2:
				add = unigram_backoff_lang2[prev_word]
			elif isLang1(prev_word) and prev_word in unigram_backoff_lang1:
				add = unigram_backoff_lang1[prev_word]
			print_test_ppl(key, unigram_logprob_lang2[key]+add, debug)
			return unigram_logprob_lang2[key]+add

		# OOV
		else:
			base = unigram_logprob_lang2["<unk>"]
			if isLang2(prev_word) and prev_word in unigram_backoff_lang2:
				base += unigram_backoff_lang2[prev_word]
			elif isLang1(prev_word) and prev_word in unigram_backoff_lang1:
				base += unigram_backoff_lang1[prev_word]
			print_test_ppl("<unk_lang2>", base, debug)
			return base

# Add to unigram dictionaries
def add_to_unigram(words, primary_lang):
	
	if primary_lang == "lang1":
		unigram_logprob_lang1[ words[1] ] = float(words[0])
		if len(words) > 2:
			unigram_backoff_lang1[ words[1] ] = float(words[2])
	elif primary_lang == "lang2":
		unigram_logprob_lang2[ words[1] ] = float(words[0])
		if len(words) > 2:
			unigram_backoff_lang2[ words[1] ] = float(words[2])

# Add to bigram dictionaries
def add_to_bigram(words, primary_lang):

	key = words[1] + "_" + words[2]
	if primary_lang == "lang1":
		bigram_logprob_lang1[ key ] = float(words[0])
		if len(words) > 3:
			bigram_backoff_lang1[ key ] = float(words[3])
	elif primary_lang == "lang2":
		bigram_logprob_lang2[ key ] = float(words[0])
		if len(words) > 3:
			bigram_backoff_lang2[ key ] = float(words[3])

# Read a lm file and store in dictionaries
def read_lm(filename, primary_lang):

	file = open(filename, 'r')

	read_gram = 0
	for line in file:

		if line == "\n" or line.startswith("\\end"):
			continue

		if line.startswith("\\1-grams:"):
			read_gram = 1
			continue
		elif line.startswith("\\2-grams:"):
			read_gram = 2
			continue

		# unigram
		if read_gram == 1:
			words = line.split()
			add_to_unigram(words, primary_lang)

		# bigram
		if read_gram == 2:
			words = line.split()
			add_to_bigram(words, primary_lang)

	file.close()

lang1_lm = sys.argv[1]		# <LANG1> Tokenized file
lang2_lm = sys.argv[2]		# <LANG2> Tokenized file
testfilename = sys.argv[3]	# Test file on which ppl needs to be calculated
debug = int(sys.argv[4])	# Set to 1 if debugging required

read_lm(lang1_lm, "lang1")
read_lm(lang2_lm, "lang2")

logprob_ratios_lang1 = calc_ratios("lang1")
logprob_ratios_lang2 = calc_ratios("lang2")

total_logprob = 0.0
total_tokens = 0

testfile = open(testfilename, 'r')
for line in testfile:

	words = line.split()
	words.append("</s>")

	start_prob = get_start_prob(words[0], debug)

	prev2_word = "<s>"
	prev_word = words[0]

	tokens = 1
	for i in range(len(words) - 1):
		next_prob = get_next_prob( prev2_word, prev_word, words[i+1], debug )
		start_prob += next_prob
		prev2_word = words[i]
		prev_word = words[i+1]
		if next_prob != 0:
			tokens += 1

	total_logprob += start_prob
	total_tokens += tokens

	ppl = pow(10, - start_prob / tokens )

	# Uncomment if you want each line and ppl to be printed
	# print line + "PPL = " + str(ppl) + "\n"

total_ppl = pow(10, - total_logprob / total_tokens )
print "------------------------------\n"
print "Total PPL: " + str(total_ppl) + "\n"
