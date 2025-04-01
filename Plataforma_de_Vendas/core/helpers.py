from nanoid import generate


def generate_unique_id():
    return generate(size=12)
