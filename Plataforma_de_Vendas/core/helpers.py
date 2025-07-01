from nanoid import generate

##########################
# MODEL HELPER FUNCTIONS #
##########################


def generate_unique_id():
    return generate(size=12)


############################
# TESTING HELPER FUNCTIONS #
############################


def convert_prices_dict(prices):
    """Convert prices dict to a list of dicts with 'price' and 'units' keys."""
    return [
        {"price": float(value), "units": int(key)}
        for key, value in sorted(prices.items(), key=lambda item: int(item[0]))
    ]
