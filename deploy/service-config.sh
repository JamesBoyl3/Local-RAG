#!/bin/bash

function update_service() {
	grep -qxF "${2}" "${3}" || \
	sed -i "s|@${1}@|${2}|g" "${3}"
}

function set_env() {
	grep -qxF "${1}=${2}" /etc/environment || \
	echo "${1}=${2}" | sudo tee -a /etc/environment
}

