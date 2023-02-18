Real Estate HousePrice Prediction
===================================

## Software and account Requirement
1. [Github Account](https://github.com/)
2. [Heroku Account](https://id.heroku.com/login)
3. [VS Code IDE](https://code.visualstudio.com/download)
4. [GIT CLI](https://git-scm.com/downloads)


## Setup
Create a conda environment
```
conda create -p venv python==3.7 -y
```

Activate conda environment
```
conda activate venv/
```

To install requirement file
```
pip install -r requirements.txt
```

* Add files to git  `git add .` or  `git add <file_name>`    
* To check the git status  `git status`    
* To check all version maintained by git  `git log`    
* To create version/commit all changes by git  `git commit -m "message"`    
* To send version/changes to github  `git push origin main`    

To setup CI/CD pipeline in Heroku, we need following info
```
1. HEROKU_EMAIL = malleswari.gelli@gmail.com
2. Heroku_API_KEY =  <>  
>-- finds in account settings, API key, Reveal, copy the key and use
3. HEROKU_APP_NAME = apptest1
```

Build docker image
```
docker build -t <image_name>:<tagname>
>note: Image name for docker must be lowercase
```

To list docker images
```
docker images
```
command to run docker image
```
docker run -p 5000:5000 -e PORT=5000 7012484a6658 # image id
```

To check running container in docker
```
docker ps
```

To stop docker container
```
docker stop <container_id or IMAGE_Id> 
```

```
python setup.py install
```

```
pip install -e . 
> -e. takes care of installing all the packages in the current directory having __init__.py method. Example housing package
> result: Successfully installed housinginsurance-predictor-0.0.3
```

```
pip install -r requirements.txt
> installs all external libraries exist (i.e in requirements.txt file)
> result: install numpy, pandas, sklearn etc libraries from requirements.txt file
```

Install ipykernel
```
pip install ipykernel
```

Data drift:
Wen your dataset stats gets change, call it as data drift
Generate statistics of train and test data sets, if stats are same bet two DATA DRIFT = 0; if there is significant difference, there is data drift

Install Evidently library
```
pip install evidently
```

