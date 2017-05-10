#!/bin/bash

base='profiles'
testsuites=(
  "cb"
  "csli"
  "ecoc"
  "ecos"
  "ecpa"
  "ecpr"
  "fracas"
  "hike"
  "jh0"
  "jh1"
  "jh2"
  "jh3"
  "jh4"
  "jh5"
  "jhk"
  "jhu"
  "mrs"
  "psk"
  "ps"
  "psu"
  "rondane"
  "rtc000"
  "rtc001"
  "sc01"
  "sc02"
  "sc03"
  "tg1"
  "tg2"
  "tgk"
  "tgu"
  "trec"
  "vm6"
  "vm13"
  "vm31"
  "vm32"
  "ws01"
  "ws02"
  "ws03"
  "ws04"
  "ws05"
  "ws06"
  "ws07"
  "ws08"
  "ws09"
  "ws10"
  "ws11"
  "ws12"
  "ws13"
)

mkdir -p out
for ts in ${testsuites[*]}; do
    echo "Converting $base/$ts" >&2
    python3 mrs_to_penman.py \
        -i "$base/$ts" \
        -p parameters.json \
        > out/$ts.txt 2>err.txt
done
