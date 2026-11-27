def merge_sort_parcels(parcels):
    """
    Sorts parcels using Merge Sort in O(n log n) time.
    Primary key: deadline (ascending - earliest deadline first)
    Secondary key: priority (descending - highest priority first)
    """
    if len(parcels) <= 1:
        return parcels

    mid = len(parcels) // 2
    left = merge_sort_parcels(parcels[:mid])
    right = merge_sort_parcels(parcels[mid:])

    return _merge(left, right)


def _merge(left, right):
    sorted_list = []
    i = j = 0

    while i < len(left) and j < len(right):
        # Earlier deadline comes first; if tied, higher priority comes first
        if (left[i]["deadline"], -left[i]["priority"]) <= (
            right[j]["deadline"],
            -right[j]["priority"],
        ):
            sorted_list.append(left[i])
            i += 1
        else:
            sorted_list.append(right[j])
            j += 1

    sorted_list.extend(left[i:])
    sorted_list.extend(right[j:])
    return sorted_list