
def hyphenate(cls, value):
    assert '_' not in value, f"Use hyphens instead of underscores in {value}"
    return value


def maxlen(max):
    def maximum_length(cls, value):
        assert len(value) <= max, f"Length of {value} must be less than {max}"
        return value
    return maximum_length


def minlen(min):
    def minimum_length(cls, value):
        assert len(value) >= min, f"Length of {value} must be more than {min}"
        return value
    return minimum_length
