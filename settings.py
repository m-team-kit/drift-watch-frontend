import os

class Config:    
    monitoring_url = os.environ.get('monitoring_url')
    monitoring_url = "http://0.0.0.0:5000"    
    