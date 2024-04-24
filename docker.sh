#!/bin/bash

# 列出所有正在运行的容器的 ID
containers=$(docker ps -q)

# 循环遍历每个容器并重启它们
for container in $containers
do
    docker stop $container
done

echo "所有容器已重启完成"
#secret