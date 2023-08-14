## Simple API for work with text files and archives

### Requirements
- Python 3.11
- Flask
- Docker
- SQLAlchemy

### Installation
```bash
$ git clone https://github.com/BohdanLazaryshyn/svit_task/tree/master
$ cd svit_task
$ python -m venv venv
$ venv\Scripts\activate (on Windows)
$ source venv/bin/activate (on macOS)
$ pip install -r requirements.txt
$ flask run
```

### Features
- Upload file
- Search file by date and keywords
- Register user and login

### Docker(for create image and run container)
docker build -t <your_name> . 
docker run -p 5000:5000 <your_name>