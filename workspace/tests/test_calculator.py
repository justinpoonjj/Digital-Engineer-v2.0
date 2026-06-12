from calculator import add, divide, multiply, subtract


def test_add():
    """Test that the add function works correctly."""
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
    assert add(-1, -1) == -2


def test_subtract():
    """Test that the subtract function works correctly."""
    assert subtract(5, 3) == 2
    assert subtract(1, 1) == 0
    assert subtract(0, 5) == -5
    assert subtract(-1, -1) == 0


def test_multiply():
    """Test that the multiply function works correctly."""
    assert multiply(2, 3) == 6
    assert multiply(-2, 3) == -6
    assert multiply(0, 5) == 0
    assert multiply(-2, -3) == 6


def test_divide():
    """Test that the divide function works correctly."""
    assert divide(6, 2) == 3
    assert divide(9, 3) == 3
    assert divide(-6, 2) == -3
    assert divide(0, 5) == 0
    assert divide(-6, -2) == 3
