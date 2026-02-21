from celery import current_app as app


@app.task
def prefetch_demo_data():
    """Prefetch demo data for testing"""
    # Implementation here
    pass
