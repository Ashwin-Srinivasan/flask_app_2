Create and activate a conda environment with all the necessary dependencies by:
conda env create -f environment.yml
conda activate flask_app

To run Flask on your localhost: 
export FLASK_APP=test2.py
export FLASK_ENV=development
flask run

Finally, open upload.html to run the application. 