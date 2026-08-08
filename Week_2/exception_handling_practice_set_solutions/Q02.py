top_reps = ["A. Chen", "R. Patel", "M. Silva", "K. Osei"]
quota_hit = {"A. Chen": 112, "R. Patel": 98, "M. Silva": 87} # % of quota

def rep_at_rank(rank):
    """Return the sales rep at a given 1-based rank."""
    try:
        return top_reps[rank- 1]
    except IndexError:
        return f"There's no one at the rank {rank}"

def quota_for(rep):
    """Return the quota-attainment % for a rep."""
    try: 
        return quota_hit[rep]
    except KeyError:
        return f"Rep {rep} doesn't exist"

def safe_report(rank, rep):
    """Bonus: use ONE 'except LookupError' block to guard BOTH
    top_reps[rank - 1] and quota_hit[rep], then print both results."""
    try:
        rep_on_rank = top_reps[rank-1]
        rep_quota = quota_hit[rep]
        return f'\nrep at rank {rank}: {rep_on_rank} rep quota: {rep_quota}'
    except LookupError:
        return "enter valid input"
    pass

print(rep_at_rank(2))
print(rep_at_rank(10))
print(quota_for("M. Silva")) # 87
print(quota_for("J. Doe"))
print(safe_report(2, "M. Silva"))
print(safe_report(10, "M. Silva"))
print(safe_report(2, "joe"))
