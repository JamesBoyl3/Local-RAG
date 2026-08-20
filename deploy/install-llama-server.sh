#!/bin/bash

set -ex

if [[ $EUID -ne 0  ]]; then
	echo "Run with sudo"
	exit 1
fi 


NVIDIA_GPU=false
AMD_GPU=false
FORCE_CPU=false
LLAMA_SERVER_BIN=""

while [[ $# -gt 0  ]]; do
	case "$1" in
		--force-cpu)
		FORCE_CPU=true
		shift 1
		;;
		--LLAMA-SERVER) 
		LLAMA_BIN="$2"
		shift 2
		;;
		*)
		shift 1
	esac
done

#Checking if GPU exists. If not forces CPU Build
if lspci | grep -qi "vga\|3d\|2d" && ! $FORCE_CPU; then 
	if lspci | grep -qi "nvidia"; then 
		NVIDIA_GPU=true
	elif lspci | grep -qi "amd"; then
		AMD_GPU=true
	fi
else;
	FORCE_CPU=true
fi


#Checking CMake exists
if ! command -v cmake >/dev/null 2>&1; then 
	echo "Cmake not found. Installing..."
	sudo apt update
	sudo apt install -y cmake
fi

#Checking llama.cpp exists
LLAMA_DIR="$HOME/llama.cpp"
if [[ -d "$LLAMA_DIR/.git" ]]; then
	echo "Llama.cpp found. Pulling..."
	git -C "$LLAMA_DIR" pull
else;
	echo "Llama.cpp not found. Cloning..."
	git clone --depth 1 https://github.com/ggml-org/llama.cpp.git "$LLAMA_DIR"
fi

#Building LLAMA-SERVER
if $FORCE_CPU; then
	echo "Forced CPU build. Building...\n"
	cmake -B "$LLAMA_DIR/build"
	cmake --build "$LLAMA_DIR/build" --config Release -j $(nproc)

elif $NVIDIA_GPU; then
	echo "Detected NVIDIA GPU. Building..."
	#Installing GCC
	if ! command -v gcc >/dev/null 2>&1; then 
		echo "GCC not found. Installing..."
		sudo apt update
		sudo apt install -y gcc
	fi 
	#Installing NVIDEA Toolkit
	if ! command -v nvcc >/dev/null 2>&1; then
  		echo "CUDA Toolkit not found. Installing..."
		if [[ ! -f "$HOME/cuda/cuda.deb" ]]; then
    			echo "NVIDIA Toolkit not found. Fetching... "
			mkdir -p "$HOME/cuda"
    			wget -O "$HOME/cuda/cuda.deb" https://developer.download.nvidia.com/compute/cuda/...
  		fi
  		sudo dpkg -i "$HOME/cuda/cuda.deb"
  		sudo cp /var/cuda-repo-debian13-13-3-local/cuda-*-keyring.gpg /usr/share/keyrings/
  		sudo apt-get update
  		sudo apt-get -y install cuda-toolkit-13-3
	fi
	export PATH="/usr/local/cuda/bin:$PATH"
	export LD_LIBRARY_PATH="/usr/local/cuda/lib64:$LD_LIBRARY_PATH"
	cmake -B "$LLAMA_DIR/build" -DGGML_CUDA=ON
	cmake --build "$LLAMA_DIR/build" --config Release

elif $AMD_GPU; then 
	echo "Detected AMD GPU. Building... (Currently not Implemented)"
else; 
	echo "Building Vulkan build... (Currently not Implemented)"
fi


