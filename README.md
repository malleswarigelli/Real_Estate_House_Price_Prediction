**REGRESSION_pipeline**
=======================



*Start Machine Learning Project*

software & tools requirements
```
1. [Github Account] (https://github.com)
2. [Heroku Account] (https://dashboard.heroku.com/login)
3. [VS_Code_IDE] (https://code.visualstudio.com/download)
4. [GIT cli] (https://git-scm.com/downloads)

5. create a new environment

```
conda create -p venv python == 3.9.2 -y
```

6. activate environment created

```
conda activate venv/
```

NOTE:
```
1. To add files to git: git add .
2. To ignore file or folder: add file/folder name to .gitignore
3. To check git status: git status
4. To check all versions maintained by git: git log
5. To create version/commit: git commit -m "first commit"
6. To send changes to git: git push origin main
7. To check remote url; git remote -v
6. git remote add origin https:github.com/malleswarigelli/drgrd.git
```

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
> result: Successfully installed housing-predictor-0.0.2
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

