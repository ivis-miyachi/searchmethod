apt-get update
apt-get install -y graphviz
pip install pygraphviz
pip install eralchemy2
eralchemy2 -i postgresql://postgres:postgres@db:5432/methoddb -o erd3.pdf