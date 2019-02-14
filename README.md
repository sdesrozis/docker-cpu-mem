# Objectif

L'objectif de ce projet est de tester les limitations cpu/mem des conteneurs docker. C'est un point important à considérer dans le cadre par exemple du déploiement d'un serveur jupyterhub sous docker.

Pour les limitations des conteneurs, voir [ici](https://docs.docker.com/config/containers/resource_constraints/#configure-the-default-cfs-scheduler).

# Construction de l'image

    docker build -t mnist:1.0 .

# En ligne de commande

Pour lancer sans limitation :

    docker run --name nolimit mnist:1.0

On vérifie avec la commande docker stats :

    > docker stats
    CONTAINER ID        NAME                CPU %               MEM USAGE / LIMIT     MEM %
    ef6f5fe71834        nolimit             506.06%             431.8MiB / 3.702GiB   11.39%

Attention, la précision de l'information 'CPU %' est à relativiser par comparaison à la commande 'top' qui est plus précise :

    > top
      PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                                     
    24701 root      20   0 2021096 499644  46320 S 375,5 12,9   3:22.83 python3                                                     

Pour plus de précision, voir [ici](https://forums.docker.com/t/docker-stats-vs-top-not-equal/39527), [ici](https://serverfault.com/questions/735246/how-does-docker-stats-output-relate-to-top-output) ou encore [ici](https://github.com/moby/moby/issues/10824).

Pour limiter le nombre de cpu :

    docker run --name cpu2.5 --cpus=2.5 mnist:1.0

On vérifie :

    CONTAINER ID        NAME                CPU %               MEM USAGE / LIMIT     MEM %
    4bf6d2de268d        cpu2.5              302.57%             440.1MiB / 3.702GiB   11.61%

et :

     PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                                     
    26060 root      20   0 2009116 505460  47208 S 253,2 13,0   0:21.99 python3                                                     

Pour limiter la mémoire :

    docker run --name memory1Go --memory 1G  mnist:1.0

On vérifie :

    CONTAINER ID        NAME                CPU %               MEM USAGE / LIMIT   MEM %
    fe9919fd29bb        memory1Go           498.61%             465.5MiB / 1GiB     45.46%

Pour savoir s'il manque des choses pour la gestion de la mémoire et du swap dans le noyau, on peut utiliser le script [suivant](https://github.com/moby/moby/blame/master/contrib/check-config.sh). 

Pour limiter la mémoire et le swap :

    docker run --name memoryswap10Mo --memory 10M --memory-swap 10M  mnist:1.0

Pour qu'un conteneur ne swappe pas et soit arrêté s'il n'a plus de mémoire :

    docker run --name noswap --memory 200M --memory-swappiness 0  mnist:1.0

# Partage par défaut des ressources CPU entre conteneur

La politique par défaut de partage des ressources entre conteneur est par défaut équilibré. Par exemple, si 3 conteneurs tournent en même temps, ils auront 33% de la capacité CPU :

    docker run -d --name cpu_1 mnist:1.0	  
    docker run -d --name cpu_2 mnist:1.0
    docker run -d --name cpu_3 mnist:1.0

    CONTAINER ID        NAME                CPU %               MEM USAGE / LIMIT     MEM %
    ef6f5fe71834        cpu_1               202.43%             405.9MiB / 3.702GiB   10.71%
    ad1ab411a37e        cpu_3               198.74%             411MiB / 3.702GiB     10.84%
    cb1539795311        cpu_2               214.89%             410.4MiB / 3.702GiB   10.83%

      PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                                     
    23932 root      20   0 2063472 486064  47240 S 138,1 12,5   0:15.80 python3                                                     
    23466 root      20   0 2031648 480600  47208 S 131,1 12,4   2:00.49 python3                                                     
    23651 root      20   0 2052132 481936  47236 S 125,5 12,4   1:30.34 python3                                                     

et si on arrête un conteneur, les deux conteneurs restant vont se répartir les ressources libérées :

    CONTAINER ID        NAME                CPU %               MEM USAGE / LIMIT     MEM %
    ef6f5fe71834        cpu_1               290.23%             408.7MiB / 3.702GiB   10.78%
    cb1539795311        cpu_2               284.47%             424.4MiB / 3.702GiB   11.20%

      PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                                     
    23932 root      20   0 2029604 479264  47240 S 195,3 12,3   0:49.62 python3                                                     
    23466 root      20   0 2031648 475664  47208 S 194,0 12,3   2:34.45 python3                                                     

En utilisant l'option '--cpu-shares', la répartition des ressources peut être modifiée. La valeur de référence par défaut est 1024. 
    
    docker run -d --cpu-shares 2048 --name cpu_1 mnist:1.0	  
    docker run -d --name cpu_2 mnist:1.0
    docker run -d --name cpu_3 mnist:1.0

Ici, le conteneur 'cpu_1' aura environ 50% des ressources et les autres 25% :

    CONTAINER ID        NAME                CPU %               MEM USAGE / LIMIT     MEM %
    1ab9f030e382        cpu_3               168.01%             405.4MiB / 3.702GiB   10.69%
    18084f90e3bf        cpu_2               185.10%             427.7MiB / 3.702GiB   11.28%
    408c566a6145        cpu_1               244.10%             426.6MiB / 3.702GiB   11.25%

      PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                                     
    26501 root      20   0 2007068 498860  47208 S 171,8 12,9   1:16.65 python3                                                     
    26613 root      20   0 2023452 467524  47236 S 110,3 12,0   0:38.88 python3                                                     
    26685 root      20   0 2000932 478480  47340 S 109,3 12,3   0:30.68 python3                                                     

Si le conteneur 'cpu_3' est arrêté, le conteneur 'cpu_1' aura 66% des ressources contre 33% pour 'cpu_2' :

    CONTAINER ID        NAME                CPU %               MEM USAGE / LIMIT     MEM %
    18084f90e3bf        cpu_2               216.85%             425.8MiB / 3.702GiB   11.23%
    408c566a6145        cpu_1               354.49%             408.8MiB / 3.702GiB   10.78%

      PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND
    26501 root      20   0 2110568 524176  47208 S 226,9 13,5   2:57.47 python3
    26613 root      20   0 2023452 478284  47236 S 164,1 12,3   1:48.75 python3                                                     

# Utilisation du SDK docker en python

Le SDK n'implémente pas l'option --cpus (version docker >= 1.13) mais les options --cpu-period et --cpu-quota permettent d'obtenir le même résultat (version docker <= 1.12). En résumé, on a cpu = cpu-quota / cpu-period et cpu-period=100000.

    >>> import docker
    >>> client = docker.from_env()
    >>> client.containers.run("mnist:1.0", detach=False, mem_limit="1G", mem_swappiness=0, cpu_period=100000, cpu_quota=150000)

# Par script

Le script run.py lance une image via le SDK en posant les limites de mémoire et cpu. Il est nécessaire d'avoir le SDK docker et docopt.
