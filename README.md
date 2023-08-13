"# svit_task" 
docker build -t docker-logs . 
docker run -p 5000:5000 docker-logs