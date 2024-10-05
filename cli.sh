if [ -f venv/bin/activate ]; then
    source venv/bin/activate
elif [ -f venv/Scripts/activate ]; then
    source venv/Scripts/activate
fi
python spacew/cli.py $@
