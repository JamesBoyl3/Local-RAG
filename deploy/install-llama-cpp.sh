#!/bin/bash

set -e

NVIDEA_GPU=false
AMD_GPU=false
LLAMA_BIN=false

while [[ $# -gt 0 ]]; do
	case "$1" in 
		-C | --CPU-build) 
		CPU_BUILD=true
		shift 1
		;;
		--NVIDEA)
		NVIDEA_GPU=true
		shift 1
		;;
		--AMD)
		AMD_GPU=true
		shift 1
		;;
		--llama-bin)
		LLAMA_BIN="$2"
		shift 2
		;;
	esac
done


#Installing llama.cpp
if [[ ! -d "$HOME/llama.cpp" && ! $LLAMA_BIN]]; then
	git clone https://github.com/ggml-org/llama.cpp.git "$HOME/llama.cpp" --depth=1
fi


#Installing CMake
if [[ ! command -v cmake >/dev/null 2>&1]]; then
	echo "CMake not found. Installing... "
	sudo apt update
	sudo apt install -y cmake
fi

#Deciding to build CPU or GPU build
if lspci | grep -i 'vga\|3d\|2d' && [[ ! $CPU_BUILD ]] ; then
	
	if lspci | grep -i 'nvidia'; then
		NVIDEA_GPU=true

	elif lspci | grep -i 'amd\|ati'; then 
		AMD_GPU=true
	
	else; then
		CPU_BUILD=true
	fi
	
fi


#Building llama-server with CPU or GPU
if [[ $CPU_BUILD ]]; then
	echo "NO GPU DETECTED..."
	echo "BUILDING CPU BUILD..."
	#Code to build CPU build
	
	cmake -B $HOME/llama.cpp/build
	cmake --build $HOME/llama.cpp/build --config Release

elif [[ $NVIDEA_GPU ]]; then
	echo "Detected NVIDEA GPU..."
	#Code for NVIDEA Build
	#Installing CUDA Toolkit
	if [[ command -v nvcc >/dev/null 2>&1 ]]; then
		echo "CUDA Toolkit not found. Installing..."
		wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb
		sudo dpkg -i cuda-keyring_1.1-1_all.deb
		sudo apt update
		sudo apt install -y cuda-toolkit
	fi 

	cmake -B $HOME/llama.cpp/build -DDGML_CUDA=ON
	cmake --build $HOME/llama.cpp/build --config Release

elif [[ $AMD_GPU ]]; then
	echo "Detected AMD GPU"
	#COde for AMD GPU
	#Installing ROCm 
	if [[ command -v hipconfig >/dev/null 2>&1  ]]; then
		wget https://repo.amd.com/rocm/packages-multi-arch/gpg/rocm.gpg -O - | \
		gpg --dearmor | \
		sudo tee /etc/apt/keyrings/amdrocm.gpg > /dev/null

		sudo tee /etc/apth/sources.lits.d/rocm.list << EOF
		deb [arch=amd64 signed-by=/etc/apt/keyrings.amdrocm.gpg] https://repo.amd.com/rocm/packages-multi-arch/debian12 stable main

		sudo apt update
		sudo apt install -y amdrocm7.14
	fi 
	
	HIPCXX="$(hipconfig -l)/clang" HIP_PATH="$(hipconfig -R)" \
    	cmake -S . -B $HOME/llama.cpp/build -DGGML_HIP=ON -DGPU_TARGETS=gfx1030 -DCMAKE_BUILD_TYPE=Release \
    	&& cmake --build $HOME/llama.cpp/build --config Release -- -j 16 
fi


exit 0
