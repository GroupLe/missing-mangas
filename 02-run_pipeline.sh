# Runs pipeline of matching grouple readmanga and grouple
# mintmanga with remanga and mangalib

python3 matcher.py configs/config_gmanga_remanga.yaml
python3 matcher.py configs/config_gmanga_mangalib.yaml

python3 matcher.py configs/config_gmint_remanga.yaml
python3 matcher.py configs/config_gmint_mangalib.yaml

python3 matcher.py configs/config_selfmanga_remanga.yaml
python3 matcher.py configs/config_selfmanga_mangalib.yaml