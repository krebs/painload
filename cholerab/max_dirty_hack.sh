#!/bin/sh
stty -echo cbreak -ofdel
x_max=90
y_max=10
x_cur=1
y_cur=1
y=
t=1
outputfile=/tmp/cholerab_out
inputfile=/tmp/cholerab_in
echo -n "c"

while [ $t -lt $(( y_max+2 )) ];do
    echo -e "[$t;$(( x_max+1 ))Hx"
    t=$(( t+1 ))
done
t=1
while [ $t -lt $(( x_max+2 )) ];do
    echo -e "[$(( y_max+1 ));${t}Hx"
    t=$(( t+1 ))
done

echo -n "[$y_cur;${x_cur}H"
#Main Loop
while x="`dd bs=1 count=1 2>/dev/null`"; do
    y="$y$x"
    case "$y" in
        (*"[A")
            if [[ $y_cur -le 1 ]];then
                y_cur=$y_max
                echo -n "[$y_cur;${x_cur}H"
            else
                echo -n "[A"
                y_cur=$(( y_cur-1 ))
            fi
            y=
            ;;
        (*"[B")
            if [[ $y_cur -ge $y_max ]];then
                y_cur=1
                echo -n "[$y_cur;${x_cur}H"
            else
                echo -n "[B"
                y_cur=$(( y_cur+1 ))
            fi
            y=
            ;;
        (*"[C")
            if [[ $x_cur -ge $x_max ]];then
                x_cur=1
                echo -n "[$y_cur;${x_cur}H"
            else
                echo -n "[C"
                x_cur=$(( x_cur+1 ))
            fi
            y=
            ;;
        (*"[D")
            if [[ $x_cur -le 1 ]];then
                x_cur=$x_max
                echo -n "[$y_cur;${x_cur}H"
            else
                echo -n "[D"
                x_cur=$(( x_cur-1 ))
            fi
            y=
            ;;
        (*"")
            if [[ $x_cur -le 1 ]];then
                x_cur=$x_max
                echo -n "[$y_cur;${x_cur}H"
            else
                echo -n "[D [D"
                x_cur=$(( x_cur-1 ))
            fi
            y=
            ;;
        (|\[)
            :
            ;;
        (*)
            if [[ $x_cur -ge $x_max ]];then
                x_cur=1
                echo -n "[$y_cur;${x_cur}H"
            else
                echo -n "$x"
                echo "<0 $x $x_cur $y_cur>" >> $outputfile
                x_cur=$(( x_cur+1 ))
            fi
            y=
            ;;
    esac
    while [[ -s $inputfile ]]; do
        cat $inputfile | head -n 1 | sed 's,[<>],,g' | { read MODE CHAR XN YN ; echo -n "7[$YN;${XN}H$CHAR8"; }
        sed -i -e "1d" $inputfile
    done

    state=`echo -n "$x" | od -An -tx | tr -d "[$IFS]"`
    echo -n "7[1;$(( x_max+2 ))H$state8"
    echo -n "7[2;$(( x_max+2 ))H             8"
    echo -n "7[2;$(( x_max+2 ))H$x_cur:$y_cur8"
done
