# hackathon_03


```
$ python3 -V
```

Python 3.9.6

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt
```

## APIキーの設定
```
$ cp .env.sample .env
```

```
HF_TOKEN=
PINECONE_API_KEY=
```

```
$ streamlit run app.py
```