# STL-LRA Analysis

## Environment Setup

* Install Miniconda from https://docs.conda.io/en/latest/miniconda.html
```shell script
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    sh Miniconda3-latest-Linux-x86_64.sh
```

* Create conda environment
```shell script
    conda update conda
    conda env create --prefix ./env -f environment.yml
```

* Install LibreOffice

    * Linux    
    ```shell script
      sudo snap install libreoffice
    ```