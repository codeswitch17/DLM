file3=$1	# Destination Directory
file4=$2	# Root directory of srilm
train_file=$3	# Train File
dev_file=$4	# Dev File
test_file=$5	# Test File

rm -rf $file3

# Train
mkdir -p $file3"/Train_Data/System_A"
cp $train_file $file3"/Train_Data/System_A/combined.txt"

# Dev
mkdir -p $file3"/Dev_Data/System_A"
cp $dev_file $file3"/Dev_Data/System_A/combined.txt"

# Test
mkdir -p $file3"/Test_Data/System_A"
cp $test_file $file3"/Test_Data/System_A/combined.txt"

for dir in $(ls $file3)
do
    mkdir -p $file3"/"$dir"/System_B_man"
    mkdir -p $file3"/"$dir"/System_B_eng"
    python clean_for_lm.py $file3"/"$dir"/System_A/combined.txt" $file3"/"$dir"/System_B_eng/combined.txt" $file3"/"$dir"/System_B_man/combined.txt" "<ENG>" "<MAN>"
done

for dir in $(ls $file3/Train_Data)
do
	./$file4/ngram-count -lm $file3/Train_Data/$dir/train.lm -text $file3/Train_Data/$dir/combined.txt -kndiscount -unk -interpolate -order 2    
done

echo "Training Perplexities:"
for dir in $(ls $file3/Train_Data)
do
	echo $dir
	./$file4/ngram -lm $file3/Train_Data/$dir/train.lm -ppl $file3/Train_Data/$dir/combined.txt -unk -order 2
done

echo "Dev Perplexities:"
for dir in $(ls $file3/Dev_Data)
do
	echo $dir
	./$file4/ngram -lm $file3/Train_Data/$dir/train.lm -ppl $file3/Dev_Data/$dir/combined.txt -unk -order 2
done

echo "Test Perplexities:"
for dir in $(ls $file3/Test_Data)
do
	echo $dir
	./$file4/ngram -lm $file3/Train_Data/$dir/train.lm -ppl $file3/Test_Data/$dir/combined.txt -unk -order 2
done

echo "Combined Perplexities:"
for dir in $(ls $file3)
do
	echo $dir
	python ../code/getPerplexity_combined.py $file3/Train_Data/System_B_man/train.lm $file3/Train_Data/System_B_eng/train.lm $file3/$dir/System_A/combined.txt 0
done
