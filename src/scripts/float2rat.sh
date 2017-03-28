
if [ $# -eq 0 ] 
then
    echo "[Error] No file supplied"
    exit 1
fi

# Prepare result file
out=/tmp/tmp_$(basename $1)
cp $1 $out

# Remove non significative zeros (not complete)
sed -i tmp -E 's/([0-9]*\.[1-9]*)0* /\1 /g' $out

# Do replacements
sed -i tmp 's/0\.5 /\(\/ 1 2\) /g' $out

sed -i tmp 's/0\.333333333333 /\(\/ 1 3\) /g' $out
sed -i tmp 's/0\.666666666667 /\(\/ 2 3\) /g' $out

sed -i tmp 's/0\.25 /\(\/ 1 4\) /g' $out
sed -i tmp 's/0\.75 /\(\/ 3 4\) /g' $out

sed -i tmp 's/0\.2 /\(\/ 1 5\) /g' $out
sed -i tmp 's/0\.4 /\(\/ 2 5\) /g' $out
sed -i tmp 's/0\.6 /\(\/ 3 5\) /g' $out
sed -i tmp 's/0\.8 /\(\/ 4 5\) /g' $out

sed -i tmp 's/0\.166666666667 /\(\/ 1 6\) /g' $out
sed -i tmp 's/0\.833333333333 /\(\/ 5 6\) /g' $out

sed -i tmp 's/0\.142857142857 /\(\/ 1 7\) /g' $out
sed -i tmp 's/0\.285714285714 /\(\/ 2 7\) /g' $out
sed -i tmp 's/0\.428571428571 /\(\/ 3 7\) /g' $out
sed -i tmp 's/0\.571428571429 /\(\/ 4 7\) /g' $out
sed -i tmp 's/0\.714285714286 /\(\/ 5 7\) /g' $out
sed -i tmp 's/0\.857142857143 /\(\/ 6 7\) /g' $out

sed -i tmp 's/0\.125 /\(\/ 1 8\) /g' $out
sed -i tmp 's/0\.375 /\(\/ 3 8\) /g' $out
sed -i tmp 's/0\.625 /\(\/ 5 8\) /g' $out
sed -i tmp 's/0\.875 /\(\/ 7 8\) /g' $out

sed -i tmp 's/0\.1 /\(\/ 1 10\) /g' $out
sed -i tmp 's/0\.9 /\(\/ 9 10\) /g' $out

cat $out && rm $out