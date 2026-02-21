from celery import current_app as app


@app.task
def batch_score_properties(property_ids: list):
    """Score a batch of properties"""
    # Implementation here
    pass
