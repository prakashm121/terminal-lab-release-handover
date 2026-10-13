FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Install essential terminal tools required for the lab
# nano, less, bsdmainutils (column), diffutils, coreutils, tree
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
        python3 \
        python3-pip \
        nano \
        less \
        bsdmainutils \
        diffutils \
        coreutils \
        curl \
        tree \
    && pip3 install --no-cache-dir fpdf \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set standard environment variables
ENV TERM=xterm-256color
ENV PAGER=less
ENV EDITOR=nano

# Ensure bash history is enabled and formatted nicely for interactive exercises
RUN echo 'export HISTTIMEFORMAT="%F %T "' >> /etc/bash.bashrc \
    && echo 'export HISTSIZE=5000' >> /etc/bash.bashrc \
    && echo 'export HISTFILESIZE=10000' >> /etc/bash.bashrc
