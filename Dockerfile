FROM centos

CMD ["pip install -r requirements.txt"]

CMD ["python eleme.py"]
