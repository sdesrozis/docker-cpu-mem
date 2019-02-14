"""
Usage:
  run.py --image=<img> [--cpus=<cpus>] [--memory=<mem>] [--no-swap]
  run.py -h | --help
  run.py --version

Options:
  -h --help       Show this screen.
  --version       Show version.
  --memory=<mem>  Memory dedicated [default: 1G].
  --cpus=<cpus>   CPU ratio [default: 2.5].
  --no-swap       Disable swap.

"""
from docopt import docopt

arguments = docopt(__doc__, version='Run Docker 1.0')

print("* image  = %s" % arguments["--image"])

print("* cpus   = %s" % arguments["--cpus"])
print("* memory = %s" % arguments["--memory"])
print("* swap   = %s" % arguments["--no-swap"])

import docker

client = docker.from_env()

swap = int(arguments["--no-swap"] == True) * 100

period = 100000
quota = int(float(arguments["--cpus"]) * period)

try:

    image = client.images.get(arguments["--image"])

    client.containers.run(image,
                          detach=False,
                          mem_limit=arguments["--memory"],
                          mem_swappiness=swap,
                          cpu_period=period,
                          cpu_quota=quota)
    
except docker.errors.ImageNotFound:
    print("image not found")

except docker.errors.APIError:
    print("docker API error...")

