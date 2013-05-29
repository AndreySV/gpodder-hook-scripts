#!/bin/bash


function check_software()
{
    local program="$1"
    which $program > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        show_message "$program is not installed on your system"
        exit 1
    fi
}


function show_message()
{
    message=$1
    echo $message
    notify-send -i /usr/share/pixmaps/gpodder.png -t 10000 -u critical "gPodder mp3_to_ogg converter:" "$message"
}


function check_ogg_file()
{
    check_software ogginfo

    ogginfo "$1"
    if [ $? -ne 0 ]; then
        return 1
    fi
    return 0
}




function check_ogg_length()
{
    local input="$1"
    local output="$2"
    local speed="$3"
    local speed_delta=0.02
    
    check_software soxi
    check_software mp3info

    # local in_len=$( soxi -D "$input" )
    local in_len=$( mp3info -p "%S" "$input" )
    local out_len=$( soxi -D "$output" )
    local need_len=$( echo "( $in_len/$speed )/1" | bc  )
    local need_len_min=$( echo "( $need_len*(1-$speed_delta) )/1" | bc  )
    local need_len_max=$( echo "( $need_len*(1+$speed_delta) )/1" | bc  )
    out_len=$( echo "$out_len/1" | bc )

    if [ 0 -eq 1 ]; then
        echo -----------------------------------------
        echo $in_len
        echo $out_len
        echo $need_len
        echo $need_len_min
        echo $need_len_max
        echo -----------------------------------------
    fi

    if [ $need_len_min -gt $out_len -o $need_len_max -lt $out_len ]; then
        show_message "Wrong length of audio file ($out_len s). Need $need_len s."
        exit 1
    fi
    return 0
}





#*****************************************************************
#
# make all check of parameter and input file
#
#*****************************************************************

check_software "notify-send"

if [ "$1" == "" ]; then 
    show_message "Error: missing input parameter."
    echo 
    echo Convert mp3 to ogg
    echo Using: mp3_to_ogg.sh input_mp3_file
    exit 1
fi

if ! [ -e "$1" ]; then
    show_message "Error: file $1 does not exist"
    exit 1
fi


if [ -d "$1" ]; then
    show_message "Error: file $1 is directory"
    exit 1
fi


logfile=/tmp/mp3_to_ogg.log
exec &>> $logfile

echo '-----------------------------------------'
sleep 2



#*****************************************************************
#
#		 is input file Mp3?
#
#*****************************************************************



no_mp3=1 
res=$(file "$1" | grep 'MPEG ADTS, layer III' )
if [ "$res" == "" ]; then
    echo "Info: input file $1 is not a MP3 audio file (check1)"
    file "$1"
else
    format=.mp3
    no_mp3=0 
fi

res=$(file "$1" | grep 'Audio' | grep 'ID3' )
if [ "$res" == "" ]; then
    echo "Info: input file $1 is not a MP3 audio file (check2)"
    file "$1"
else
    format=.mp3
    no_mp3=0 
fi

#*****************************************************************
#
#		 is input file OGG?
#
#*****************************************************************

no_ogg=0 
res=$(file "$1" | grep 'Vorbis audio'  )
if [ "$res" == "" ]; then
    echo Info: input file $1 is not a OGG audio file
    file "$1"
    no_ogg=1 
else
    format=.ogg
fi

if [ "$no_ogg" == "1" -a "$no_mp3" == "1" ]; then
    echo unsupported format
    show_message "File $1 has unsupported format"
    exit 1
fi;

echo Format = $format

#*****************************************************************

tmp_file=${1}_tmp$format
new_name=$( echo $1 | sed 's/mp3/ogg/' )
mv "$1" "$tmp_file"

#*****************************************************************
#
#		 check tags in  mp3 file
#
#*****************************************************************

if [ "$format" = ".mp3" ]; then
    
    check_software mid3iconv

    # convert ID3v1 supported only 8-bit codepages to
    # ID3v2 with UTF-8 support. 
    source_encoding=CP1251
    # source_endcoding=ISO8859-1

    mid3iconv --encoding $source_encoding --dry-run "$tmp_file"
    if [ $? -ne 0 ]; then
        show_message "mid3iconv is failed on dry run"
        exit 1
    fi
    mid3iconv --encoding $source_encoding "$tmp_file"
fi

#*****************************************************************
#
#		 check input mp3 file
#
#*****************************************************************

if [ "$format" = ".mp3" ]; then

    check_software mp3check
    check_software mp3val


    mp3check_opt=
    mp3check_opt="${mp3check_opt} -e"     # 
    mp3check_opt="${mp3check_opt} -G"     # to suppress error message when IdV3 Tag exists
    mp3check_opt="${mp3check_opt} -B"     # to enable VBR support
    mp3check_opt="${mp3check_opt} -S"     # ignomre junk before first frame
                                          # usually this is ID3v2 tag, 
                                          # which is not supported by mp3check
    mp3check_opt="${mp3check_opt} -W"     # to ignore switching
                                          # constant parameters like a sampling frequency

    mp3check $mp3check_opt "$tmp_file"
    if [ $? -ne 0 ]; then
        

        # --cut-junk-start can't be used. It removed ID3v2 tags 
        # as result mp3 tags are unreadable
        mp3check $mp3check_opt --cut-junk-end "$tmp_file"

        mp3check $mp3check_opt "$tmp_file"
        if [ $? -ne 0 ]; then
            # repair audio stream
            mp3val -f "$tmp_file"
            rm "$tmp_file.bak"
            echo 
        fi
        
        mp3check $mp3check_opt "$tmp_file"
        if [ $? -ne 0 ]; then
            show_message "Input mp3 file $tmp_file seems to be currupted. Please redownload it."
            exit 1
        fi
    fi
fi


#*****************************************************************
#
#               Converting using sox utility
#
#*****************************************************************

check_software sox

# allows to see transfer function of the compressor or any 
# other effect

# DEBUG_EFFECTS=1

if [ "$DEBUG_EFFECTS" != "" ];  then
    DEBUG_EFFECTS_OPTIONS=" --plot gnuplot "
    new_name=" --null " 
    DEBUG_TRANSF_FUNC_FILE=/tmp/mp3_to_ogg.plt
else
    DEBUG_TRANSF_FUNC_FILE=/tmp/mp3_to_ogg.sox.log
fi

#***************************************************************

EFFECTS=

# the main effect of the chain - compressor. 
# it reduce dynamic range of the input audio to hear in a noisy 
# environment

EFFECTS=$EFFECTS" compand 0.1,0.3 6:-60,-30,-15,-20,-12,-4,-8,-2,-7 -2 -90 0.2 "
# EFFECTS=$EFFECTS" compand 0.2,1 6:-80,-70,-15,0,-3 -2 -90 0.2"

# time-stretcing
EFFECT_TEMPO_SPEED=1.25
EFFECTS=$EFFECTS" tempo -s $EFFECT_TEMPO_SPEED "

# EFFECTS=$EFFECTS" norm "
# EFFECTS=$EFFECTS" dither -f "

#***************************************************************

OPTIONS=
OPTIONS=${OPTIONS}" $DEBUG_EFFECTS_OPTIONS "
OPTIONS=$OPTIONS" --guard "     	# protect file agains clipping


# OPTIONS=$OPTIONS" --single-threaded "
OPTIONS=$OPTIONS" --multi-threaded --buffer 131072 "

OPTIONS=$OPTIONS" -v 0.98 "    		# to avoid clipping
OPTIONS=$OPTIONS" --temp /tmp "

INPUT=
INPUT=$INPUT" -t $format "
INPUT=$INPUT" \"$tmp_file\" "


QUALITY=" -C 5 "
#***************************************************************

try=0
max_try=3
echo
echo "Converting file $tmp_file using sox..."

while true; do
    try=$(( $try + 1 ))
    if [ $try -gt $max_try ]; then 
        show_message "sox failed $max_try times during converting file $tmp_file"
        exit 1
    fi

    echo "Try #$try"
    sox $OPTIONS -t $format "$tmp_file" -t.ogg $QUALITY "$new_name" $EFFECTS > $DEBUG_TRANSF_FUNC_FILE
    if [ "$DEBUG_EFFECTS_OPTIONS" == "" ]; then cat $DEBUG_TRANSF_FUNC_FILE; fi;


    if [ $? -eq 0  ]; then
        # sometimes sox returns 0, but output file is broken 
        
        # check correction of ogg file
        check_ogg_file "$new_name"
        if [ $? -ne 0 ]; then
            echo "Resulting ogg file seems to be broken"
            continue
        fi
        
        # check length of converted audio in compare to source file
        check_ogg_length "$tmp_file" "$new_name" "$EFFECT_TEMPO_SPEED"
        if [ $? -eq 0 ]; then
            echo "File is successfully converted"
            break
        fi
    else
        # sox returns 2 when plot options is given.
        # it's a little bit strange
        if [ "$DEBUG_EFFECTS" != "" ];  then break; fi;
    fi

done

if [ "$DEBUG_EFFECTS" != "" ];  then
    check_software gnuplot

    gnuplot $DEBUG_TRANSF_FUNC_FILE
fi


#*****************************************************************
#
#		 cleaning old files
#
#*****************************************************************
rm "$tmp_file"
exit 0

