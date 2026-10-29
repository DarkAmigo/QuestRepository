import pytest

from service_body_test import Order

@pytest.mark.parametrize(
    ("items", "expected_total"),
    [
        ([], 0),
        ([{"price": 10, "quantity": 2}], 20),
        ([{"price": 3.5, "quantity": 2}, {"price": 4, "quantity": 3}], 19),
        ([{"price": 0, "quantity": 5}, {"price": 12, "quantity": 0}], 0),
    ],
)
def test_total_for_various_item_sets(items, expected_total):
    assert Order(1, items).total() == expected_total


def test_most_expensive_returns_highest_price_item():
    cheapest = {"price": 5, "quantity": 10}
    expensive = {"price": 25, "quantity": 1}
    middle = {"price": 12, "quantity": 3}
    assert Order(2, [cheapest, expensive, middle]).most_expensive() is expensive


def test_most_expensive_returns_first_item_when_prices_tie():
    first = {"price": 10, "quantity": 1}
    second = {"price": 10, "quantity": 2}
    assert Order(3, [first, second]).most_expensive() is first


def test_most_expensive_raises_error_for_empty_items():
    with pytest.raises(ValueError):
        Order(4, []).most_expensive()


@pytest.mark.parametrize(
    ("percent", "expected_prices"),
    [
        (0, [100, 40, 0]),
        (25, [75, 30, 0]),
        (100, [0, 0, 0]),
    ],
)
def test_apply_discount_changes_price_of_every_item(percent, expected_prices):
    items = [
        {"price": 100, "quantity": 1},
        {"price": 40, "quantity": 2},
        {"price": 0, "quantity": 5},
    ]
    order = Order(5, items)

    order.apply_discount(percent)

    assert [item["price"] for item in items] == pytest.approx(expected_prices)


@pytest.mark.parametrize("percent", [-1, 101, -0.01, 100.01])
def test_apply_discount_rejects_invalid_percentages(percent):
    items = [{"price": 20, "quantity": 2}]
    order = Order(6, items)

    with pytest.raises(ValueError, match="Invalid discount"):
        order.apply_discount(percent)

    assert items[0]["price"] == 20


def test_apply_discount_on_empty_items_is_valid():
    order = Order(7, [])
    order.apply_discount(50)
    assert order.items == []
    assert order.total() == 0


def test_repr_for_order_with_items():
    order = Order("ABC", [{"price": 10, "quantity": 2}, {"price": 5, "quantity": 1}])
    assert repr(order) == "<Order ABC: 2 items>"


def test_repr_for_empty_order():
    assert repr(Order(8, [])) == "<Order 8: 0 items>"