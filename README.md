# Twitter Text Processor

Twitter Text Processor (TTP) is a software that converts a tweet into its textual form by a series of operations.
It also extracts emotional information from the resulting text.

To install the tool, just run:
```
pip install -r requirements.txt
```

If you use SpaCy, you also need to download the models:
```
spacy download en_core_web_lg
spacy download it_core_news_lg
...
```
Finally, you can run the server:
```
python3 server.py
```

Authors: Stefano Menini ([menini@fbk.eu](mailto:menini@fbk.eu)) and Alessio Palmero Aprosio ([aprosio@fbk.eu](mailto:aprosio@fbk.eu)).
