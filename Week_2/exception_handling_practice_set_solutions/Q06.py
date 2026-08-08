accounts = {
    "ACC-1001": 5000.0,
    "ACC-1002": 250.0,
    "ACC-1003": 0.0,
}

class InsufficientFundsError(Exception):
    pass

class InvalidAmountError(Exception):
    pass


def withdraw(account_id, amount):
    """Withdraw 'amount' from an account and return the new balance."""
    if amount > 0:
        if amount < accounts[account_id]:
            withdrawn_amount = accounts[account_id] - amount
            accounts[account_id] -= amount
            return withdrawn_amount
        else:
            raise InsufficientFundsError(f"insufficient funds in account with account id: {account_id}")
    else:
        raise InvalidAmountError("Withdrawal amount must be positive") 

def process_withdrawal(account_id, amount):
    try:
        amount_reduced = withdraw(account_id, amount)
        print(f"{amount} withdrawn from account id: {account_id}")
        print(f'new balance: {accounts[account_id]}')
    except Exception as e:
        print(e)
    


# --- Test cases ---
process_withdrawal("ACC-1001", 1200)
process_withdrawal("ACC-9999", 100)
process_withdrawal("ACC-1002", -50)
process_withdrawal("ACC-1003", 100)