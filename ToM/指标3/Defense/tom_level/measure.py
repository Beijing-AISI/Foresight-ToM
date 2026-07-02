"""
ToM level measurement using Hi-ToM benchmark ordering.

ToM Level corresponds to the highest consecutive Order (0–4) where the model
achieves >= threshold accuracy.  Order N roughly maps to N-th order belief
reasoning ("X thinks Y thinks Z thinks …").
"""


class ToMOrder:
    """Result of a Hi-ToM evaluation — highest passing Order or fail."""

    def __init__(self, highest_passing_order):
        """
        Args:
            highest_passing_order: int 0-4 if some order passed, None if even
                                   Order 0 was not passed.
        """
        self._order = highest_passing_order

    @property
    def passed(self) -> bool:
        return self._order is not None

    @property
    def to_m_level(self) -> int:
        """
        Integer representation:
            0  = fail (cannot pass Order 0)
            1  = 0th-order ToM (grasps direct reality)
            2  = 1st-order ToM (tracks one agent's belief)
            ...
            5  = 4th-order ToM (highest Hi-ToM level)
        """
        if self._order is None:
            return 0
        return self._order + 1

    def __str__(self):
        if self._order is None:
            return "ToMOrder(fail) — cannot even pass Order 0"
        return (
            f"ToMOrder({self._order}) — highest passing Order {self._order} "
            f"(ToM level {self.to_m_level})"
        )

    def __repr__(self):
        return str(self)


def level_from_joint_accuracy(
    joint_accuracy: dict,
    tell: str,
    length: int,
    threshold: float = 50.0,
) -> ToMOrder:
    """
    Derive ToM level from per-order accuracy entries.

    Args:
        joint_accuracy: nested dict keyed as
            {f"Tell: {tell}": {f"Length {length}, Order {N}": {"accuracy": float, ...}}}
        tell:      "No_Tell" or "Tell"
        length:    1, 2, or 3 (story length in Hi-ToM)
        threshold: minimum accuracy (%) required to pass an order (default 50)

    Returns:
        ToMOrder representing the highest consecutive passing order (starting
        from Order 0).  If Order 0 does not pass, returns ToMOrder(None).
    """
    tell_key = f"Tell: {tell}"
    orders_data = joint_accuracy.get(tell_key, {})

    highest_passing = None
    for order in range(5):  # 0 … 4
        order_key = f"Length {length}, Order {order}"
        entry = orders_data.get(order_key)
        if entry is None:
            break  # no data for this order — stop here
        accuracy = entry.get("accuracy", 0.0)
        if accuracy >= threshold:
            highest_passing = order
        else:
            break  # chain broken — stop (must be consecutive from Order 0)

    return ToMOrder(highest_passing)
