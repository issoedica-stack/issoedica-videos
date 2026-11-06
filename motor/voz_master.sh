#!/bin/sh
# Masterização da narração (voz clonada do Bom, ElevenLabs v4). Aprovada pelo Bom em 06/11/2026.
# Uso: sh motor/voz_master.sh entrada.mp3 saida.wav
ffmpeg -y -hide_banner -loglevel error -i "$1" -af "highpass=f=75,lowpass=f=15000,equalizer=f=220:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=2.5,equalizer=f=7000:t=q:w=2:g=-2.5,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,loudnorm=I=-14:TP=-1.2:LRA=7" -ar 48000 "$2"
