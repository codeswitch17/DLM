import os
import sys

def write_list_to_file(filename, wordlist):
	for i in range(len(wordlist)):
		word = wordlist[i]

		filename.write(word)
		if i != len(wordlist) - 1:
			filename.write(" ")
		else:
			filename.write("\n")

def ngrams(input, n):
	output = []
	for i in range(len(input)-n+1):
		output.append(input[i:i+n])
	return output

# Check if word is from language 1
# NOTE - Provide your own function depending on the language you are working on
def isLang1( word ):

	if word == "":
		return 1

	start_bracs = [ '(', '[' ]
	if ord(word[0]) < 123 and (word[0] not in start_bracs):
		return 1
	elif word[0] in start_bracs and word != "()" and word != "[]":
		return isLang1(word[1:])
	else:
		return 0

in_file = open(sys.argv[1], 'r')
cleaned_lang1_file = open(sys.argv[2], 'w')
cleaned_lang2_file = open(sys.argv[3], 'w')
lang1_token = sys.argv[4]
lang2_token = sys.argv[5]

for line in in_file:

	new_line_lang1 = []
	new_line_lang2 = []
	is_prev_lang1 = False
	is_prev_lang2 = False

	words = line.split()
	for word in words:

		if isLang1(word):

			new_line_lang2.append(word)
			if is_prev_lang1 == False:
				new_line_lang1.append(lang1_token)

			is_prev_lang1 = True
			is_prev_lang2 = False
		else:

			new_line_lang1.append(word)
			if is_prev_lang2 == False:
				new_line_lang2.append(lang2_token)

			is_prev_lang1 = False
			is_prev_lang2 = True

	write_list_to_file(cleaned_lang1_file, new_line_lang1)
	write_list_to_file(cleaned_lang2_file, new_line_lang2)

in_file.close()
cleaned_lang1_file.close()
cleaned_lang2_file.close()
