# Gene-ius
Full stack web application with Flask REST API for backend, and React/Typescript for frontend with persisting Redis NoSQL database integration on Kubernetes for querying and returning interesting information from HGNC data published by The Human Genome Organization (HUGO).
The application is currently under development.

The repository includes Dockerfile for protability, and included Docker Compose to automate deployment. In addition, there are six yaml files to deploy the app on a kubernetes cluster, which aids in container ochestration.

## Data Description
The Human Genome Organization (HUGO) is a non-profit which oversees the HUGO Gene Nomenclature Committee (HGNC). The HGNC "approves a unique and meaningful name for every gene".

The complete HGNC dataset file, available in both tab separated and JSON formats, are archived monthly and quarterly. For this project, we are using the "Current JSON format hgnc_complete_set file". It contains a set of all approved gene symbol reports found on the GRCh38 reference and the alternative reference loci.

The data has 54 columns, and some columns are sparsely populated. Below are a brief overview of some fields:
| Field Name              | Description                                                         |
| ----------------------- | ------------------------------------------------------------------- |
| hgnc_id                 | HGNC ID. A unique ID created by the HGNC for every approved symbol. |
| symbol                  | The HGNC approved gene symbol. Equates to the "APPROVED SYMBOL" field within the gene symbol report. |
| name                    | HGNC approved name for the gene. Equates to the "APPROVED NAME" field within the gene symbol report. |
| locus_group             | A group name for a set of related locus types as defined by the HGNC (e.g. non-coding RNA). |
| locus_type              | The locus type as defined by the HGNC (e.g. RNA, transfer). |
| status                  | Status of the symbol report, which can be either "Approved" or "Entry Withdrawn". |
| location                | Cytogenetic location of the gene (e.g. 2q34). |
| location_sortable       | Same as "location" but single digit chromosomes are prefixed with a 0 enabling them to be sorted in correct numerical order (e.g. 02q34). |
| date_approved_reserved  | The date the entry was first approved. |

More details about the dataset used can be found in the [HGNC complete set archive](https://www.genenames.org/download/archive/) website.

## Implementation
The project uses **Python 3.8.10**, in particular **Flask 2.2.2**, **redis 4.5.1** and **Docker 20.10.12** for containerization. 

### Files
* `Dockerfile` -- commands for building a new image
* `docker-compose.yml` -- container application management
* `gene_api.py` -- python scripts for the Flask application
* `README.md` -- project documentation

In addition, there are six files in the `kubernetes` folder for container ochestration and deployment:
* `dwi67-deployment-python-debug.yml`
* `dwi67-test-pvc.yml`
* `dwi67-test-flask-deployment.yml`
* `dwi67-test-redis-deployment.yml`
* `dwi67-test-flask-service.yml`
* `dwi67-test-redis-service.yml`

## Installation

You have the option to build this project from source, or use the provided Docker container on DockerHub. A Docker installation is required, as we build and run a Docker image.

We describe below the installation process using terminal commands, which are expected to run on a Ubuntu 20.04.5 machine with Python3. Installation may differ for other systems.

**Source build using docker-compose file provided in this repository is highly recommended as it automates your deployment process to a single step**

<details>
<summary><h3>Source build (option 1)</h3></summary>

Since this is a Docker build, the requirements need not be installed, as it will automatically be done on the Docker image. All commands, unless otherwise noted, are to be run in a terminal (in the `homework06` directory of the cloned repository).

* First, install Docker: `sudo apt-get install docker` or follow installation instructions for [Docker Desktop](https://www.docker.com/get-started/) for your system. We are using **Docker 20.10.12**
* Next, install docker-compose: `sudo apt-get install docker-compose-plugin` or follow the instructions [here](https://docs.docker.com/compose/install/linux/). We are using **Docker Compose 1.25.0**
* Clone the  repository: `git clone https://github.com/dhannywi/COE332.git`
* Then, change directory into the `homework08` folder: `cd ./homework08/`


### **Option 1:** Automate deployment using `docker-compose`
The quickest way to get your services up and running is to use `docker-compose` to automate deployment.
* Create a `data` folder inside the `homework08` directory. Execute `mkdir data`. This allows redis to store data in the disk so that the data persist, even when the services are killed.
* Execute `docker-compose up --build`. Your images are built and services are up and running when you see this message:
```console
username:$ docker-compose up --build
Creating network "homework08_default" with the default driver
Building flask-app
...
...
Successfully built 8a67666a6b16
Successfully tagged dhannywi/gene-ius:kube
Creating homework08_redis-db_1 ... done
Creating homework08_flask-app_1 ... done
Attaching to homework08_redis-db_1, homework08_flask-app_1
redis-db_1   | 1:C 13 Apr 2023 16:45:19.438 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
...
...
flask-app_1  |  * Running on all addresses (0.0.0.0)
flask-app_1  |  * Running on http://127.0.0.1:5000
flask-app_1  |  * Running on http://192.168.48.3:5000
flask-app_1  | Press CTRL+C to quit
flask-app_1  |  * Restarting with stat
flask-app_1  |  * Debugger is active!
flask-app_1  |  * Debugger PIN: 179-378-064
```

* Execute `docker ps -a`. You should see the containers running.
```console
username:$ docker ps -a
CONTAINER ID   IMAGE                    COMMAND                  CREATED          STATUS          PORTS                                       NAMES
07fdf8858de5   dhannywi/gene-ius:kube   "python gene_api.py"     12 minutes ago   Up 12 minutes   0.0.0.0:5000->5000/tcp, :::5000->5000/tcp   homework08_flask-app_1
c80cfdaab872   redis:7                  "docker-entrypoint.s…"   12 minutes ago   Up 12 minutes   0.0.0.0:6379->6379/tcp, :::6379->6379/tcp   homework08_redis-db_1
```

### **Option 2:** Build and run your own docker image
* First, create a `data` folder inside the `homework08` directory. Execute `mkdir data`. This allows redis to store data in the disk so that the data persist even when the services are killed.
* Now, build the image: `docker build -t <docker_username>/<app_name>:<version_number> .`
This output shows that your build is successful:
```console
username:$ docker build -t dhannywi/gene-ius:kube .
Sending build context to Docker daemon  58.37kB
...
...
Successfully built 54af1d1a71c4
Successfully tagged dhannywi/gene-ius:kube
```

* Check the docker images currently running in your computer by executing: `docker images`. The image you just built would show up in the list of images:
```console
username:$ docker images
REPOSITORY             TAG       IMAGE ID       CREATED             SIZE
dhannywi/gene-ius      kube      8a67666a6b16   2 minutes ago       1.06GB
redis                  7         dd786f66ff99   8 minutes ago       117MB
```

* Execute `docker-compose up` and your services is up and running when you see the message:
```console
username:$ docker-compose up
Creating network "homework08_default" with the default driver
Building flask-app
...
...
Successfully built 8a67666a6b16
Successfully tagged dhannywi/gene-ius:kube
Creating homework08_redis-db_1 ... done
Creating homework08_flask-app_1 ... done
Attaching to homework08_redis-db_1, homework08_flask-app_1
redis-db_1   | 1:C 13 Apr 2023 16:45:19.438 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
...
...
flask-app_1  |  * Running on all addresses (0.0.0.0)
flask-app_1  |  * Running on http://127.0.0.1:5000
flask-app_1  |  * Running on http://192.168.48.3:5000
flask-app_1  | Press CTRL+C to quit
flask-app_1  |  * Restarting with stat
flask-app_1  |  * Debugger is active!
flask-app_1  |  * Debugger PIN: 179-378-064
```
##
**Killing the services**

If you madea any changes to the `gene_api.py` file, you will need to kill the existing services that's running and rebuild. Execute `docker-compose down`. The services are removed when you see the following message:
```console
username:$ docker-compose down
Removing homework08_flask-app_1 ... done
Removing homework08_redis-db_1  ... done
Removing network homework08_default
```
</details>

<details>
<summary><h3>From Docker Hub (option 2)</h3></summary>

**Install**

* To install the Docker container, first install Docker: `sudo apt-get install docker` or follow installation instructions for [Docker Desktop](https://www.docker.com/get-started/) for your system. We are using Docker 20.10.12

* Next, pull the images from the docker hub and install the containers: `docker pull dhannywi/gene-ius:kube`

* Check the docker images currently running in your computer by executing: `docker images`
The image you just installed would show up in the list of images:
```console
username:$ docker images
REPOSITORY            TAG       IMAGE ID       CREATED         SIZE
dhannywi/gene-ius     kube      96ca98e4cc62   3 hours ago     1.06GB
```

**Run**

* Create a `data` folder inside the directory you are working on. Execute `mkdir data`. This allows redis to store data in the disk so that the data persist, even when the services are killed.
* Execute `docker-compose up` to automatically pull redis image, install dependencies and connect the network:
```console
username:$ docker-compose up
Creating network "homework08_default" with the default driver
Creating homework08_redis-db_1 ... done
Creating homework08_flask-app_1 ... done
...
redis-db_1   | 1:M 13 Apr 2023 20:27:21.171 * Ready to accept connections
flask-app_1  |  * Serving Flask app 'gene_api'
flask-app_1  |  * Debug mode: on
...
flask-app_1  | Press CTRL+C to quit
flask-app_1  |  * Restarting with stat
flask-app_1  |  * Debugger is active!
flask-app_1  |  * Debugger PIN: 722-563-854
```
* Check that all the services are running by executing `docker ps -a`
* When you want to kill the services, execute `docker rm -f <container id you want to kill>`
</details>

<br>

## Kubernetes Deployment
To run this app on a Kubernetes cluster, enter the following commands in the console from which you have Kubernetes access - Please follow order:
* `kubectl apply -f dwi67-test-redis-service.yml`
* `kubectl apply -f dwi67-test-pvc.yml`
* `dwi67-test-redis-deployment.yml`
* `kubectl apply -f dwi67-test-flask-service.yml`
* `kubectl apply -f dwi67-test-flask-deployment.yml`
* `kubectl apply -f dwi67-test-python-debug.yml`

You will see a confirmation message after running each command. For example:
```console
username:$ kubectl apply -f dwi67-test-flask-deployment.yml
deployment.apps/dwi67-test-flask-deployment configured
```

* Check that your services are running properly, execute `kubectl get services`
```console
username:$ kubectl get services
NAME                       TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
dwi67-test-flask-service   ClusterIP   10.233.63.169   <none>        5000/TCP   104m
dwi67-test-redis-service   ClusterIP   10.233.37.116   <none>        6379/TCP   88m
```
* Execute `kubectl get pvc` to ensure that your pvc is bound:
```console
username:$ kubectl get pvc
NAME             STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
dwi67-test-pvc   Bound    pvc-6913cf20-3f7b-4441-9acf-1216c0ca37be   1Gi        RWO            cinder-csi     18m
```
* Check that your deployments are running:
```console
username:$ kubectl get deployments
NAME                          READY   UP-TO-DATE   AVAILABLE   AGE
dwi67-test-flask-deployment   2/2     2            2           14m
dwi67-test-redis-deployment   1/1     1            1           16m
py-debug-deployment           1/1     1            1           16d
```
* To check if your pods are running and discover the IP address of your redis pod, execute the command `kubectl get pods -o wide`
```console
username:$ kubectl get pods -o wide
NAME                                          READY   STATUS    RESTARTS   AGE     IP              NODE            NOMINATED NODE   READINESS GATES
dwi67-test-flask-deployment-66bdd5dff-gjmxv   1/1     Running   0          102m    10.233.85.239   kube-worker-2   <none>           <none>
dwi67-test-flask-deployment-66bdd5dff-vc829   1/1     Running   0          102m    10.233.85.214   kube-worker-2   <none>           <none>
dwi67-test-redis-deployment-c6bcc5c74-v5t5g   1/1     Running   0          86m     10.233.85.219   kube-worker-2   <none>           <none>
py-debug-deployment-f484b4b99-hk6pb           1/1     Running   0          4h44m   10.233.85.241   kube-worker-2   <none>           <none>
```
* Alternatively, you can also execute `kubectl get all` to get pod, service, deployment and replicaset information.
* Note the python debug deployment name to access it, execute:
`kubectl exec -it py-debug-deployment-f484b4b99-hk6pb -- /bin/bash`
* It will allow you to use a bash terminal similar to:
```console
username:$ kubectl exec -it py-debug-deployment-f484b4b99-hk6pb -- bash
root@py-debug-deployment-f484b4b99-hk6pb:/# 
```
* You can test that your application is running properly by executing the `curl` commands described in usage, and it should work as expected. For example:
```console
root@py-debug-deployment-f484b4b99-hk6pb:/# curl dwi67-test-flask-service:5000/genes
[ ...,
  "HGNC:40019",
  "HGNC:46637",
  "HGNC:28630",
  "HGNC:32248"
]
```

<details>
<summary><h3>Customization for Developers</h3></summary>

* Running commands above will automatically pull the `dhannywi/gene-ius:kube` image from the docker hub.
If you wish to use your own Flask API in the kubernetes cluster, you must change the name of image being pulled in `docker-compose.yml` and `dwi67-test-flask-deployment.yml` to your preferred image on Docker Hub and then re-apply the kubernetes depolyment.
* You may also want to change the **Environment variable** in your `docker-compose.yml` to reflect your redis service name. Example:
```console
environment:
  - REDIS_IP=<redis-service-name>
```
* The same change will also need to be done on the `flask-deployment.yml`:
```console
env:
  - name: REDIS_IP
    value: <redis-service-name>
```
* **Note** the <redis-service-name> need to match the name under `redis-service.yml` metadata. Example:
```console
---
apiVersion: v1
kind: Service
metadata:
  name: <redis-service-name>
```

</details>
<br>

## Usage
Once you have the docker image running with dependencies installed and the local server running, we can start querying using the REST API in the Flask app.

There are thirteen routes for you to request data from:

|    | Route | Method | What it returns |
| -- | ----- | ------ | --------------------- |
| 1. | `/data`   | POST | Put data into Redis   |
| 2. | `/data` | GET | Return all data from Redis |
| 3. | `/data` | DELETE | Delete data in Redis |
| 4. | `/genes` | GET | Return json-formatted list of all hgnc_ids |
| 5. | `/genes/<hgnc_id>` | GET | Return all data associated with <hgnc_id> |
| 6. | `/image` | POST | Create plot and saves it to Redis |
| 7. | `/image` | GET | Return plot image to the user, if present in the database |
| 8. | `/image` | DELETE | Delete the plot image from the database |

### Querying HGNC data using the REST API
Since we need to keep the server running in order to make requests, open an additional shell and change your directory to the same directory your server is running. The data has been automatically loaded and you can start querying. Keep in mind that if you accidentally queried using the `DELETE` method, you will need to query using the `POST` method first in order to re-load the dataset into the database. Otherwise, when data has not been loaded/ has been deleted, you will receive an error message. For example:
```console
username:$ curl dwi67-test-flask-service:5000/genes
No data in db
```

The `/data` route has 3 methods: `GET`, `POST`, and `DELETE`. The first time you are running the services you will need to use the `POST` method to load data into the database. 

#### 1. Route `/data` with `POST` method
Execute the command `curl dwi67-test-flask-service:5000/data -X POST` on your terminal. This may take a while, data has been successfully loaded into db when you see the message:
```console
username:$ curl dwi67-test-flask-service:5000/data -X POST
Data loaded
```

#### 2. Route `/data` with `GET` method
If you want the App to return all the available data in the database, execute `curl dwi67-test-flask-service:5000/data`. Your output will be similar to below:
```console
username:$ curl dwi67-test-flask-service:5000/data
[
  ...,
  {
    "_version_": 1761599366515130368,
    "agr": "HGNC:2769",
    "alias_symbol": [
      "DRP",
      "DRP1",
      "SMAP-3"
    ],
    "ccds_id": [
      "CCDS45003"
    ],
    "date_approved_reserved": "1999-06-17",
    "date_modified": "2023-01-20",
    "date_name_changed": "2016-07-04",
    "ena": [
      "AF038554"
    ],
    "ensembl_gene_id": "ENSG00000139726",
    "entrez_id": "8562",
    "hgnc_id": "HGNC:2769",
    "location": "12q24.31",
    "location_sortable": "12q24.31",
    "locus_group": "protein-coding gene",
    "locus_type": "gene with protein product",
    "mane_select": [
      "ENST00000280557.11",
      "NM_003677.5"
    ],
    "mgd_id": [
      "MGI:1915434"
    ],
    "name": "density regulated re-initiation and release factor",
    "omim_id": [
      "604550"
    ],
    "prev_name": [
      "density-regulated protein"
    ],
    "pubmed_id": [
      9628587,
      16982740,
      20713520,
      27239039
    ],
    "refseq_accession": [
      "NM_003677"
    ],
    "rgd_id": [
      "RGD:1584200"
    ],
    "status": "Approved",
    "symbol": "DENR",
    "ucsc_id": "uc001uda.4",
    "uniprot_ids": [
      "O43583"
    ],
    "uuid": "e4eba18a-f927-44a7-83f3-85dd42410234",
    "vega_id": "OTTHUMG00000168844"
  }
]
```
#### 3. Route `/data` with `DELETE` method
When you wish to delete existing data in the database, execute `curl localhost:5000/data -X DELETE`

Database is cleared when you see the message:
```console
username:$ curl dwi67-test-flask-service:5000/data -X DELETE
Data deleted, there are 0 keys in the db
```

#### 4. Route `/genes`
Next, we will query for a list of all the available `hgnc_id` in the data set. Execute the command `curl dwi67-test-flask-service:5000/genes` on your terminal. You should get output similar to this:

```console
username:$ curl dwi67-test-flask-service:5000/genes
[ ....,
  "HGNC:31407",
  "HGNC:1434",
  "HGNC:23105",
  "HGNC:28587",
  "HGNC:35487",
  "HGNC:55215",
  "HGNC:149",
  "HGNC:26445",
  "HGNC:13012",
  "HGNC:25762"
]
```

#### 5. Route `/genes/<hgnc_id>`
We can query for the gene data of a specific `hgnc_id` in the dataset. To do this, execute the command `curl localhost:5000/genes/<hgnc_id>` on your terminal, but replace `<hgnc_id>` with a particular id you are interested in.

For example, `curl dwi67-test-flask-service:5000/genes/HGNC:33843` results in output below:

```console
username:$ curl dwi67-test-flask-service:5000/genes/HGNC:33843
{
  "_version_": 1761599382604480512,
  "agr": "HGNC:33843",
  "alias_symbol": [
    "MGC61598"
  ],
  "ccds_id": [
    "CCDS35188"
  ],
  "date_approved_reserved": "2008-10-15",
  "date_modified": "2023-01-20",
  "date_name_changed": "2017-05-12",
  "ensembl_gene_id": "ENSG00000198435",
  "entrez_id": "441478",
  "gene_group": [
    "Ankyrin repeat domain containing"
  ],
  "gene_group_id": [
    403
  ],
  "hgnc_id": "HGNC:33843",
  "location": "9q34.3",
  "location_sortable": "09q34.3",
  "locus_group": "protein-coding gene",
  "locus_type": "gene with protein product",
  "mane_select": [
    "ENST00000356628.4",
    "NM_001004354.3"
  ],
  "mgd_id": [
    "MGI:1914372"
  ],
  "name": "NOTCH regulated ankyrin repeat protein",
  "omim_id": [
    "619987"
  ],
  "pubmed_id": [
    11485984,
    21998026
  ],
  "refseq_accession": [
    "NM_001004354"
  ],
  "rgd_id": [
    "RGD:1591939"
  ],
  "status": "Approved",
  "symbol": "NRARP",
  "ucsc_id": "uc004cmo.3",
  "uniprot_ids": [
    "Q7Z6K4"
  ],
  "uuid": "b2384d06-afcc-482a-aafd-cbfb6b11e357",
  "vega_id": "OTTHUMG00000156150"
}
```

However, if you request an invalid id, for example `curl dwi67-test-flask-service:5000/genes/abc`, you will get:
```console
username:$ curl dwi67-test-flask-service:5000/genes/abc
hgnc_id requested is invalid.
```

#### 6. `/image` route with `POST`
To create a bar chart of all the gene locus group in the HGNC database:
```console
username:$ curl dwi67-test-flask-service:5000/image -X POST
Plot saved to db.
```

#### 7. `/image` route with `GET`
To retrieve the chart created from the `POST` command and transfer it from the Redis database to a user's current directory on their machine, execute the command as below:
```console
username:$ curl dwi67-test-flask-service:5000/image --output myimage.png
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 25089  100 25089    0     0  21684      0  0:00:01  0:00:01 --:--:-- 21684
```
However, you will get a `Plot not in db, pls execute "POST" method to create plot.` error if you have not executed the `POST` method.

#### 8. `/image` route with `DELETE`
To delete the image from the database, run command as below:
```console
username:$ curl dwi67-test-flask-service:5000/image -X DELETE
Plot deleted from db.
```

## Additional Resources

* [HGNC complete set archive](https://www.genenames.org/download/archive/)

## Authors

Dhanny W Indrakusuma<br>
dhannywi@utexas.edu
