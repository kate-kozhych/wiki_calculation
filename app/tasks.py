# from celery import Celery

# app = Celery('tasks', broker='redis://localhost//')

# @app.task(blind=True)
# def calculate_pi_from_pizza(self, n):
#     self.update_state(state='PROGRESS', meta={'progress': 0.5})
#     return final_pi_value