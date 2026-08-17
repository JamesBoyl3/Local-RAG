#!/bin/bash

if [[ ! -x "$HOME/llama.cpp/build/bin/llama-bench" ]]; then 
	echo "Could not find llama-bench. Installing..."
	cmake --build  "$HOME/llama.cpp/build" --config Release --target llama-bench
fi

"$HOME/llama.cpp/build/bin/llama-bench" -m "$HOME/.cache/huggingface/hub/models--Qwen--Qwen2.5-3B-Instruct-GGUF/snapshots/7dabda4d13d513e3e842b20f0d435c732f172cbe/qwen2.5-3b-instruct-q4_0.gguf" -pg 512,128 -o md > performance$(date '+%Y-%m-%d').md
