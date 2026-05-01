def model_to_dict(model, include=None):
    data = {}
    for col in model.__table__.columns:
        if include and col.name not in include:
            continue
        val = getattr(model, col.name)
        try:
            # serialize datetimes
            data[col.name] = val.isoformat() if hasattr(val, 'isoformat') else val
        except Exception:
            data[col.name] = val
    return data
