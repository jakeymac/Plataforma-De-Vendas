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
    """Convert a product's prices dictionary to the correct format."""
    return {int(key): float(value) for key, value in prices.items()}
