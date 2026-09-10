#!/bin/bash

set -eu

source service-config.sh
 
status() { printf "${1}\n" >&1; }
warning() { printf "WARNING: ${1}\n" >&2; }
error() { printf "${1}/\n" >&2; exit 1; }


if [[ $EUID -ne 0 ]]; then
	error "Run with sudo"
fi

function main() {

	LLAMA_SERVER_BIN=""
	LLAMA_PATH="/home/rag_sys/llama-cpp"

	while [[ "${#}" -ne 0 ]]; do 

		case "${1}" in
			--force-cpu) 
				FORCE_CPU=true
				shift 1
				;;
			--llama-server-bin)
				LLAMA_SERVER_BIN="${2}"
				shift 2
				;;
			--NIVIDIA-ARCH)
				NVIDIA_ARCH="${2}"
				shift 2
				;;
			--help)
				help
			;;
			*)
				shift 1
				;;
		esac
	done

	if [[ ! -e "${LLAMA_PATH}" ]]; then 		
		llama_cpp_setup
	fi

	if ! command -v llama-server >/dev/null 2>&1; then
		LLAMA_BUILD="${LLAMA_PATH}/build"
		llama_server_setup
	fi

	if [[ ! -e "$LLAMA_PATH" ]]; then
		if [[ -e "${LLAMA_PATH}" ]]; then
			LLAMA_BUILD="${LLAMA_PATH}/build"
			which_GPU
		else
			llama_cpp_setup
			warning "llama-server has not been setup yet. Rerun this script to set it up"
		fi
	fi

	return 0
}

function llama_cpp_setup() {
	if [[ ! -d "$LLAMA_PATH" ]]; then
		git clone https://github.com/ggml-org/llama.cpp "$LLAMA_PATH"
	fi
}

function CUDA_server_setup() {
	check_cmake
        export CUDACXX="/usr/local/cuda/bin/nvcc"
        export PATH="/usr/local/cuda/bin${PATH:+:${PATH}}"
	cd "${LLAMA_PATH}"
	cmake -B "${LLAMA_BUILD}" -DGGML_CUDA=ON
	cmake --build "$LLAMA_BUILD" --config Release -t llama-server -j "$(nproc)"
}

function check_cmake() {
        if ! command -v cmake >/dev/null 2>&1; then
                sudo apt update
                sudo apt install -y cmake
        fi
}

function check_gcc() {
	if ! command -v gcc; then 
		sudo apt update
		sudo apt install -y gcc
	fi 
}

function llamaserver_setup() {
	if  lspci | grep -i nvidia; then
		if [[ ! -d  /home/rag_sys/cuda ]]; then
			get_CUDA_toolkit
		fi
		CUDA_server_setup
	fi
}

function get_CUDA_toolkit() {
	check_gcc

	wget https://developer.download.nvidia.com/compute/cuda/repos/debian13/x86_64/cuda-keyring_1.1-1_all.deb
	dpkg -i cuda-keyring_1.1-1_all.deb --root=/srv/cuda/keyrings
	sudo apt update
	sudo apt install -y cuda-toolkit
	warning "CUDA toolkit installed. System needs to be REBOOTED."
}

function help() {
	printf "Helps users set up some of the essentials to run a local RAG application.\n\n"
	printf "PREREQUISITES:\n"
	printf "git: in order to clone llama.cpp you will need git\n\n"
	printf "OPTIONS:\n"
	printf "--force-cpu\tThe script tries to detect a GPU. If you want a CPU build, use this flag to tell the script to ignore any GPU.\n"
	printf "--llama-server-bin\tUse this if you have llama.cpp setup with llama-server to avoid any duplications.\n"
	printf "--NVIDIA-ARCH\tUse this when you have an outdate NVIDIA architecture that needs a different version of CUDA.\n"
	
	exit 0
}

main "${@}"

exit 0
