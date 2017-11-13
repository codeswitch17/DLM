train_file=$1	# Train File
dev_file=$2		# Dev File
test_file=$3	# Test File

. ./path.sh

tmpdest="/tmp/testing"	# Temporary Destination Directory
rm -rf $tmpdest

# Train
mkdir -p $tmpdest"/Train_Data/System_A"
cp $train_file $tmpdest"/Train_Data/System_A/combined.txt"

# Dev
mkdir -p $tmpdest"/Dev_Data/System_A"
cp $dev_file $tmpdest"/Dev_Data/System_A/combined.txt"

# Test
mkdir -p $tmpdest"/Test_Data/System_A"
cp $test_file $tmpdest"/Test_Data/System_A/combined.txt"

for dir in $(ls $tmpdest)
do
    mkdir -p $tmpdest"/"$dir"/System_B_lang2"
    mkdir -p $tmpdest"/"$dir"/System_B_lang1"
    python clean_for_lm.py $tmpdest"/"$dir"/System_A/combined.txt" $tmpdest"/"$dir"/System_B_lang1/combined.txt" $tmpdest"/"$dir"/System_B_lang2/combined.txt" "<LANG1>" "<LANG2>"
done

for dir in $(ls $tmpdest/Train_Data)
do
	./$SRILM_ROOT/ngram-count -lm $tmpdest/Train_Data/$dir/train.lm -text $tmpdest/Train_Data/$dir/combined.txt -kndiscount -unk -interpolate -order 2    
done

echo "Training Perplexities:"
for dir in $(ls $tmpdest/Train_Data)
do
	echo $dir
	./$SRILM_ROOT/ngram -lm $tmpdest/Train_Data/$dir/train.lm -ppl $tmpdest/Train_Data/$dir/combined.txt -unk -order 2
done

echo "Dev Perplexities:"
for dir in $(ls $tmpdest/Dev_Data)
do
	echo $dir
	./$SRILM_ROOT/ngram -lm $tmpdest/Train_Data/$dir/train.lm -ppl $tmpdest/Dev_Data/$dir/combined.txt -unk -order 2
done

echo "Test Perplexities:"
for dir in $(ls $tmpdest/Test_Data)
do
	echo $dir
	./$SRILM_ROOT/ngram -lm $tmpdest/Train_Data/$dir/train.lm -ppl $tmpdest/Test_Data/$dir/combined.txt -unk -order 2
done

echo "Combined Perplexities:"
for dir in $(ls $tmpdest)
do
	echo $dir
	python get_SystemB_ppl.py $tmpdest/Train_Data/System_B_lang2/train.lm $tmpdest/Train_Data/System_B_lang1/train.lm $tmpdest/$dir/System_A/combined.txt 0
done

rm -rf $tmpdest