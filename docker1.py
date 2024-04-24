import docker

doc = docker.from_env()

containers = doc.containers.list()
for container in containers:
    if (container.name!="mysql-test" or container.name!="selenium-hub"):
        # container.stop()
        # container.start()
        container.restart()


# secret