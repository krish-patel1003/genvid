def is_owner(resource, user) -> bool:
    if resource is None or user is None:
        return False
    try:
        return resource.owner_id == user.id
    except AttributeError:
        return False
