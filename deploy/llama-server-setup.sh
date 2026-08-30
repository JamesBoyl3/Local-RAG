#!/bin/bash
function main() {
        set -eu
        if [[ $EUID -ne 0 ]]; then
                echo "Run with sudo"
                exit 1
        fi
        status() { printf "${1}" >&1; }
        error() { printf "${1}" >&2; exit 1; }
        warning() { printf "WARNING: ${1}" >&2; }

        NVIDIA_GPU=false
        AMD_GPU=false
        FORCE_CPU=false
        LLAMA_SERVER_BIN=""

        while [[ $# -gt 0 ]]; do
                case "$1" in
                        --force-cpu)
                        FORCE_CPU=true
                        shift 1
                        ;;
                        --llama-server-bin)
                        LLAMA_SERVER_BIN="$2"
                        shift 2
                        ;;
                        *)
                        shift 1
                esac
        done

        if [[ -n "$LLAMA_SERVER_BIN" ]]; then
                if [[ -x "$LLAMA_SERVER_BIN" ]]; then
                        status "Using existing llama-server binary at $LLAMA_SERVER_BIN\n"
                        exit 0
                else
                        error "Provided --llama-server-bin path is not executable: $LLAMA_SERVER_BIN\n"
                fi
        fi

        # Checking if a GPU exists. If not, forces a CPU build.
        if lspci | grep -qi "vga\|3d\|2d" && ! $FORCE_CPU; then
                if lspci | grep -qi "nvidia"; then
                        NVIDIA_GPU=true
                elif lspci | grep -qi "amd"; then
                        AMD_GPU=true
                fi
        else
                FORCE_CPU=true
        fi

        # Checking CMake exists
        if ! command -v cmake >/dev/null 2>&1; then
                echo "Cmake not found. Installing..."
                sudo apt update
                sudo apt install -y cmake
        fi

        # Checking llama.cpp exists
        LLAMA_DIR="$HOME/llama.cpp"
        if [[ -d "$LLAMA_DIR/.git" ]]; then
                echo "Llama.cpp found. Pulling..."
                git -C "$LLAMA_DIR" pull
        else
                echo "Llama.cpp not found. Cloning..."
                git clone --depth 1 https://github.com/ggml-org/llama.cpp.git "$LLAMA_DIR"
        fi

        # Building LLAMA-SERVER
        if $FORCE_CPU; then
                echo "Forced CPU build. Building...\n"
                cmake -B "$LLAMA_DIR/build"
                cmake --build "$LLAMA_DIR/build" --config Release -j $(nproc)

        elif $NVIDIA_GPU; then
                echo "Detected NVIDIA GPU. Building..."

                # Installing GCC
                if ! command -v gcc >/dev/null 2>&1; then
                        echo "GCC not found. Installing..."
                        sudo apt update
                        sudo apt install -y gcc
                fi

                # Installing NVIDIA Toolkit
                if ! command -v nvcc >/dev/null 2>&1; then
                        echo "CUDA Toolkit not found. Installing..."

                        source /etc/os-release
                        DISTRO_TAG="${ID}${VERSION_ID//./}"  # e.g. ubuntu2204, debian12

                        mkdir -p "$HOME/cuda"
                        KEYRING_DEB="$HOME/cuda/cuda-keyring.deb"
                        if [[ ! -f "$KEYRING_DEB" ]]; then
                                echo "Fetching CUDA keyring for $DISTRO_TAG..."
                                wget -O "$KEYRING_DEB" \
                                        "https://developer.download.nvidia.com/compute/cuda/repos/${DISTRO_TAG}/x86_64/cuda-keyring_1.1-1_all.deb" \
                                        || error "Could not find a CUDA repo for detected distro '$DISTRO_TAG'. Check https://developer.nvidia.com/cuda-downloads for the correct repo name for your OS.\n"
                        fi

                        sudo dpkg -i "$KEYRING_DEB"
                        sudo apt-get update
                        sudo apt-get -y install cuda-toolkit-12-6
                fi

                export PATH="/usr/local/cuda/bin:$PATH"
                export LD_LIBRARY_PATH="/usr/local/cuda/lib64:$LD_LIBRARY_PATH"

                cmake -B "$LLAMA_DIR/build" -DGGML_CUDA=ON -DCMAKE_CUDA_ARCHITECTURES=61
                cmake --build "$LLAMA_DIR/build" --config Release -j $(nproc)

        elif $AMD_GPU; then
                echo "Detected AMD GPU. Building... (Currently not Implemented)"
        else
                echo "Building Vulkan build... (Currently not Implemented)"
        fi
}

main "$@"
