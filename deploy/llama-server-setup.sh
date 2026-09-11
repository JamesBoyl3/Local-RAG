#!/bin/bash

set -eu

##### SCRIPT SETUP #####

#Imports (Change in future for readability)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/service-config.sh"

status() { printf "${1}\n" >&1; }
warning() { printf "WARNING: ${1}\n" >&2; }
error() { printf "${1}/\n" >&2; exit 1; }

#Checking for privaleges
if [[ $EUID -ne 0 ]]; then
	error "Run with sudo"
fi

#Parsing args
while [[ "${#}" -ne 0 ]]; do

	case "${1}" in
		-t)
			TEST=true
			shift 1
			;;
		-u)
			USER="${2}"
			shift 2
			;;
		--force-cpu)
			FORCE_CPU=true
			shift 1
			;;
		--llama-server-bin)
			LLAMA_SERVER_BIN="${2}"
			shift 2
			;;
		help)
			help
			;;
		*)
			shift 1
			;;
	esac
done

##### SERVER SETUP ######
function main() {

	#Defining Basic Locations
	USER_HOME="/home/${USER}"
	LLAMA_PATH="${USER_HOME}/llama-cpp"

	#Check if llama.cpp is already installed
	if [[ ! -d "${LLAMA_PATH}" ]]; then
		llama_cpp_setup "${LLAMA_PATH}"
	fi

	#Checking if llama-server is already built
	if ! command -v llama-server >/dev/null 2>&1; then
		LLAMA_BUILD="${LLAMA_PATH}/build"
		llama_server_setup "${LLAMA_BUILD}"
	fi
}

##### BUILDING TOOLS #####
function llama_cpp_setup() {
	#Download llama.cpp
	git clone https://github.com/ggml-org/llama.cpp "${1}"
}

function llama_server_setup() {
	#Checks which GPU is available
	#Builds the correct llama-server build for that GPU
	if  lspci | grep -i nvidia; then
		if [[ ! -d "${USER_HOME}/"
		if [[ ! -d  "${USER_HOME}/cuda" ]]; then
			sudo -u "${USER}" get_CUDA_toolkit
		fi
		sudo -u "${USER}" CUDA_server_setup "${1}"
	fi
}

function CUDA_server_setup() {
	check_cmake
        export CUDACXX="/usr/local/cuda/bin/nvcc"
        export PATH="/usr/local/cuda/bin${PATH:+:${PATH}}"
	cd "${LLAMA_PATH}"
	cmake -B build -DGGML_CUDA=ON
	cmake --build build --config Release -t llama-server -j "$(nproc)"
	cd "${SCRIPT_DIR}"
}

##### GPU UTILS #####
function get_CUDA_toolkit() {
	check_gcc
	wget https://developer.download.nvidia.com/compute/cuda/repos/debian13/x86_64/cuda-keyring_1.1-1_all.deb
	dpkg -i cuda-keyring_1.1-1_all.deb --root="${USER_HOME}"
	apt update
	apt install -y cuda-toolkit
	warning "CUDA toolkit installed. System needs to be REBOOTED."
}

function get_NVIDIA_driver() {
	#https://docs.nvidia.com/datacenter/tesla/driver-installation-guide/latest/debian.html#debian-installation-network
	wget https://developer.download.nvidia.com/compute/cuda/repos/debian13/sbsa/cuda-keyring_1.1-1_all.deb
	dpkg -i cuda-keyring_1.1-1_all.deb
	apt update
	apt install nvidia-driver-pinning

	apt -V install nvidia-open
	systemctl restart nvidia-persistenced
}

function check_cmake() {
        if ! command -v cmake >/dev/null 2>&1; then
                apt update
                apt install -y cmake
        fi
}

function check_gcc() {
	if ! command -v gcc; then
		apt update
		apt install -y gcc
	fi
}

#### SERVICES BUILDING #####
function start_services() {
	update_api
	update_generative
	update_embedding
}

function update_api() {
	local SERVICE="${SCRIPT_DIR}/api-server.service"
	update_service "SERVICE_USER" "${USER}" "${SERVICE}"
	update_service "API_PATH" "${SCRIPT_DIR}/main" "${SERVICE}"
	update_service "UVICORN_PATH" "" "${SERVICE}"
}

function update_generative() {
	local SERVICE="${SCRIPT_DIR}/gerative-server.service"
	update_service "SERVICE_USER" "${USER}" "${SERVICE}"
	update_service "LLAMA-SERVER" "${LLAMA_BUILD}/bin/llama-server" "${SERVICE}"
}

function update_embedding() {
	local SERVICE="${SCRIPT_DIR}/embedding-server.service"
	update_service "SERVICE_USER" "${USER}" "${SERVICE}"
}

##### ECT #####
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

main
exit 0
