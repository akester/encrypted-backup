files=$1;
outdir=$2

x=1;
while [[ $x -le $files ]]; 
 do echo Creating file no $x;
  dd bs=1024 count=$RANDOM skip=$RANDOM if=/dev/urandom of=$outdir/random-file.$counter 1> /dev/null;
  let "x += 1";
 done
