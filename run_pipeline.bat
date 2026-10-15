cd /d C:\Users\MSI\Projets_perso\Projet1_stations_essence
echo ===== %date% %time% ===== >> data\pipeline.log
venv\Scripts\python.exe src\extract.py >> data\pipeline.log 2>&1
venv\Scripts\python.exe src\transform.py >> data\pipeline.log 2>&1
