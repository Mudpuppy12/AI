FROM mcr.microsoft.com/devcontainers/python:3

RUN apt-get update && \
    apt-get install -y xz-utils 

# Kubectl
ENV KUBECTL_VERSION=v1.31.1
RUN curl -LO https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/arm64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /usr/local/bin/kubectl

# Ansilbe
RUN pip3 install ansible && pip3 install botocore && pip install boto3

ENV ATMOS_VERSION=1.157.0
RUN curl -LO https://github.com/cloudposse/atmos/releases/download/v${ATMOS_VERSION}/atmos_${ATMOS_VERSION}_linux_arm64 && \
    chmod +x ./atmos_${ATMOS_VERSION}_linux_arm64 && \
    mv ./atmos_${ATMOS_VERSION}_linux_arm64 /usr/local/bin/atmos

RUN curl "https://s3.amazonaws.com/session-manager-downloads/plugin/latest/ubuntu_arm64/session-manager-plugin.deb" -o "session-manager-plugin.deb" && \
    dpkg -i session-manager-plugin.deb && \
    rm session-manager-plugin.deb

RUN rm -rf /var/lib/apt/lists/*

# Azure CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# Claude AI Agent
RUN npm install -g @anthropic-ai/claude-code 
