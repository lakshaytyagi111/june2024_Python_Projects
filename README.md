# june2024_Python_Projects
# Black Hat Python Projects

This repository contains a collection of projects inspired by the book "Black Hat Python" by Justin Seitz. Additionally, it includes some custom projects.

## Table of Contents

- [Introduction](#introduction)
- [Projects](#projects)
  - [Bluetooth Proxy](#bluetooth-proxy)
  - [Replacing Netcat](#replacing-netcat)
  - [TCP Proxy](#tcp-proxy)
  - [TCP Server](#tcp-server)
  - [TCP Client](#tcp-client)
  - [UDP Client](#udp-client)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

This repository showcases various network-related projects inspired by the book "Black Hat Python." The projects aim to deepen understanding of networking concepts, Python programming, and penetration testing techniques.

## Projects

### Bluetooth Proxy

**File:** `chapter_1/bluetooth_proxy.py`

This project creates a proxy that forwards audio data from a mobile device to a Bluetooth speaker via a laptop. It allows audio streaming from the mobile device to the speaker, even if the speaker does not support multiple device connections.

### Replacing Netcat

**File:** `chapter_1/replacing_netcat.py`

A Python script that mimics the functionality of the popular Netcat tool. This project demonstrates how to build a simple networking tool for reading and writing data across network connections.

### TCP Proxy

**File:** `chapter_1/tcp_proxy.py`

A simple TCP proxy written in Python. It forwards traffic between a client and a server, allowing for traffic inspection and manipulation.

### TCP Server

**File:** `chapter_1/tcp_server.py`

A basic TCP server implemented in Python. It listens for incoming connections and handles them, demonstrating how to create server-side network applications.

### TCP Client

**File:** `chapter_1/tcp_client.py`

A basic TCP client implemented in Python. It connects to a TCP server, sends data, and receives responses, demonstrating how to create client-side network applications.

### UDP Client

**File:** `chapter_1/udp_client.py`

A simple UDP client implemented in Python. It sends data to a UDP server and receives responses, illustrating the use of the UDP protocol in network communication.

## Usage

To run any of these scripts, ensure you have Python installed on your system. Then, navigate to the `chapter_1` folder and execute the desired script it will tell the usage parammeters and syntax:
requirement.txt files are provided within required chapters.

```Bash
pip install -r requirements.txt
```
